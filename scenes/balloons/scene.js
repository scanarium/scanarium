// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

// Scene: balloons

var groupBallons;
var groupBeaks;

function scene_preload() {
    game.load.image('Cloud-1', scene_dir + '/cloud1.png');
    game.load.image('Cloud-2', scene_dir + '/cloud2.png');
    game.load.image('Cloud-3', scene_dir + '/cloud3.png');
}

function spawnCloud(onCreated) {
    var flavor = tunnel(Math.floor(Math.random()*3) + 1, 1, 3)
    actorManager.addActor('Cloud', flavor, onCreated);
}

function spawnClouds(immediate = false) {
    var existing = actorManager.getActorCount('Cloud');
    var target = 20;
    var needed = target - existing;
    for (var i = 0; i < needed; i++) {
        spawnCloud(cloud => {
            if (immediate) {
                cloud.alpha = 1;
                cloud.x = Math.random() * scanariumConfig.width;
            }
        });
    }
}

function birdBalloonCollision(balloon, beak) {
    balloon.pop();
}

function scene_create() {
    Wind.init();
    actorManager.registerActor(Cloud);
    actorManager.onActorDestroy(function(actor) {spawnClouds();}, 'Cloud');
    LayoutManager.register(function() {spawnClouds(true)});

    groupBalloons = game.add.group();
    groupBeaks = game.add.group();
    game.physics.add.overlap(groupBalloons, groupBeaks, birdBalloonCollision);
}

function scene_update(time, delta) {
    Wind.update(time, delta);
}

function depthCorrectionFactor(depth) {
    return (1 + depth) / 2;
}

class WindAffectedSprite extends Phaser.Physics.Arcade.Sprite {
    constructor(x, y, flavor, width, minScale, maxScale) {
        super(game);
        const actor = this.constructor.name;
        this.flavored_actor = actor + '-' + flavor
        this.setTexture(this.flavored_actor, '__BASE');
        this.setPosition(x, y);
        game.physics.world.enable(this);
        this.depth = Math.random();
        var scale = scaleBetween(minScale, maxScale, this.depth) * refToScreen;
        var height = this.height / this.width * width * scale;
        var width = width * scale;
        this.setDisplaySize(width, height);
        // Setting collission size to half width, so we only collid if we're
        // already a bit into the balloon.
        this.setSize(this.width / 2, this.height);
        this.setFlipX(Math.random() > 0.5);
        this.destroyOffset = Math.sqrt(width * width + height * height) / 2;
        this.body.setMaxVelocityX(10 * refToScreen);
    }

    update(time, delta) {
        this.setAccelerationX(Wind.getForce(this.y) * 60 * refToScreen)
    }
}

class Cloud extends WindAffectedSprite {
    constructor(x, y, flavor) {
        super(x, y, flavor, 400, 0.2, 0.8);
        this.y = Math.random() * scanariumConfig.height;
        this.x = Math.random() * scanariumConfig.width/2;
        var force = Wind.getForce(this.y);
        if (force <=0) {
            this.x += scanariumConfig.width/2;
        }
        this.setVelocityX(force * 120 * refToScreen);
        this.destroyOffset = this.displayWidth / 2;
        this.alpha = 0;
    }

    update(time, delta) {
        super.update(time, delta);
        this.alpha += 0.01;
    }
}

class Shred extends Phaser.Physics.Arcade.Sprite {
    constructor(x, y, texture, spec, balloonSpec, depth, balloonWidth, balloonHeight) {
        super(game, x, y, texture);
        game.sys.displayList.add(this);
        game.physics.world.enableBody(this);

        var width = 2 * spec.r / balloonSpec.width * balloonWidth;
        var height =  2 * spec.r / balloonSpec.height * balloonHeight;
        this.setDisplaySize(width, height);

        this.depth = depth;

        var velocity = new Phaser.Math.Vector2(spec.x - balloonSpec.width/2, spec.y - balloonSpec.height/2);
        velocity.normalize()
            .scale(4000 * depthCorrectionFactor(this.depth) * refToScreen * randomBetween(0.8, 2))
            .rotate(randomBetween(-Math.PI/4, Math.PI/4));
        this.body.setVelocity(velocity.x, velocity.y);
        this.body.setAngularVelocity(randomBetween(-10000, 10000));
        this.body.setGravityY(140);


        const tweenDurationMin = 20;
        const tweenDurationMax = 100;

        var tweens = [];
        for (var i=0; i<5; i++) {
            const isNarrow = Math.random() > 0.5
            tweens.push({
                displayWidth: width * (isNarrow ? randomBetween(0.1, 0.3) : randomBetween(0.6, 0.9)),
                displayHeight: height * (isNarrow ? randomBetween(0.6, 0.9) : randomBetween(0.1, 0.3)),
                duration: randomBetween(tweenDurationMin, tweenDurationMax),
            });
        }
        tweens.push({
            displayWidth: 1,
            displayHeight: 1,
            duration: randomBetween(tweenDurationMin, tweenDurationMax),
        });
        this.timeline = game.tweens.timeline({
            targets: this,
            ease: 'Bounce.easeOut',
            onComplete: () => {
                this.destroy();
            },
            tweens: tweens,
        });

  }
}

class BaseBalloon extends WindAffectedSprite {
    constructor(flavor, width, x, y, spec) {
        super(x, y, flavor, width, 0.4, 1);
        this.spec = spec;
        this.y = scanariumConfig.height + this.displayHeight/2;
        this.setVelocityY(-20 * depthCorrectionFactor(this.depth) * refToScreen);
        groupBalloons.add(this);
        this.createTextures();
    }

    createTextures() {
        if (this.spec.shreds.length > 0) {
            if (!game.textures.exists(this.flavored_actor + '-shred-0')) {
                this.createTexturesForce();
            }
        }
    }

    createTexturesForce() {
      const that = this;
      const full_texture = game.textures.get(this.flavored_actor);
      const full_texture_source_index = 0;
      const full_source = full_texture.source[full_texture_source_index];
      const full_width = full_source.width;
      const full_height = full_source.height;

      this.spec.shreds.forEach((shredSpec, i) => {
          const x = shredSpec.x / this.spec.width * full_width;
          const y = shredSpec.y / this.spec.height * full_height;
          const r = shredSpec.r / this.spec.width * full_width;

          const frame_name = 'shred-' + String(i);
          var frame = full_texture.add(
              frame_name, full_texture_source_index,
              x - r, y - r, 2 * r, 2 * r);

          var eraserEraser = game.make.graphics();
          eraserEraser.fillStyle(0xffffff, 1);
          for (var i = 0; i < 360; i += 30) {
              const eR = randomBetween(0.5, 1) * r
              const eX = r + Math.cos(i * degToRadian) * eR;
              const eY = r - Math.sin(i * degToRadian) * eR;
              if (i == 0) {
                  eraserEraser.moveTo(eX, eY);
              } else {
                  eraserEraser.lineTo(eX, eY);
              }
          }
          eraserEraser.closePath();
          eraserEraser.fillPath();

          var eraser = game.make.renderTexture({
              width: 2 * r,
              height: 2 * r,
          }, false);
          eraser.fill(0xffffff, 1);
          eraser.erase(eraserEraser);

          var texture = game.make.renderTexture({
              width: 2 * r,
              height: 2 * r,
          }, false);
          texture.drawFrame(this.flavored_actor, frame_name);
          texture.erase(eraser);
          texture.saveTexture(this.flavored_actor + '-' + frame_name);
      });
    }

    update(time, delta) {
        super.update(time, delta);
        this.setAngle(this.body.velocity.x * screenToRef);
    }

    pop() {
        this.spec.shreds.forEach((shredSpec, i) => {
            const texture = this.flavored_actor + '-shred-' + String(i);
            var shred = new Shred(this.x, this.y, texture, shredSpec, this.spec, this.depth, this.displayWidth, this.displayHeight);
        });
        actorManager.deleteActor(this);
    }
}

var Wind = {
    maxForce: 0.1,
    sections: 4,
    reinitPeriod: 10 * 1000,

    init: function() {
        this.minForce = -this.maxForce;
        this.forces = [0];
        var i;
        for (i=1; i<this.sections; i++) {
            this.forces.push(0);
        }
        this.nextReinit = 0;
        this.reinit();
    },

    reinit: function() {
        var i;
        this.forces[0] = this.updateForce(this.forces[0]);
        for (i = 1; i < this.sections; i++) {
            this.forces[i] = this.updateForce((this.forces[i] + this.forces[i-1]) / 2);
        }
    },

    updateForce: function(force) {
        force += scaleBetween(this.minForce, this.maxForce, Math.random()) ;
        force = tunnel(force, this.minForce, this.maxForce);
        return force;
    },

    update: function(time, delta) {
        if (time >= this.nextReinit) {
            this.reinit();
            this.nextReinit = time + this.reinitPeriod;
        }
    },

    getForce: function(y) {
        var sectionWidth = scanariumConfig.height / this.sections;
        var section = tunnel(Math.floor(y / sectionWidth), 0, this.sections-1);
        var sectionScale = tunnel(Math.min(y / sectionWidth - section, 1), 0, 1);
        var minForce = this.forces[section];
        var maxForce = this.forces[Math.min(section+1, this.sections-1)];
        return scaleBetween(minForce, maxForce, sectionScale);
    }
}

class Wings extends Phaser.Physics.Arcade.Sprite {
  constructor(x, y, image_name, bird, body, bodySpec, coordinateCorrectionFactor) {
    super(game, x, y, image_name);

    game.physics.world.enableBody(this);
    game.sys.updateList.add(this);

    this.bird = bird;
    this.x = body.x;
    this.y = body.y + (bodySpec.wing.flapY - bodySpec.center[1]) / bodySpec.height * body.displayHeight;
    this.fullWidth = body.displayWidth;
    this.fullHeight = body.displayHeight;
    this.setOrigin(body.originX, bodySpec.wing.flapY / bodySpec.height);

    this.phase = 0;
    // 0 -- gliding
    // 1 -- from gliding to wings to top
    // 2 -- downward stroke
    // 3 -- from bottom to glide
    // 4 -- from bottom to upward
    this.phaseDurations = [
        bodySpec.wing.durations.glide,
        bodySpec.wing.durations.glideToUp,
        bodySpec.wing.durations.upToDown,
        bodySpec.wing.durations.downToGlide,
        bodySpec.wing.durations.downToUp,
    ];
    const scales = (bodySpec.wing.scales || {});
    this.targetScales = {
        'up': scales.up || 1,
        'glide': scales.center || -0.1,
        'down': scales.down || -1,
    };
    this.wingScale = 0;
    this.wingAccelerationX = 0;
    this.wingAccelerationY = 0;
    this.flapAccelerationX = bodySpec.wing.flapAcceleration[0] * bird.coordinateCorrectionFactor;
    this.flapAccelerationY = -bodySpec.wing.flapAcceleration[1] * bird.coordinateCorrectionFactor;

    this.phaseEnd = 0;
    this.update(0, 0, Math.random() > 0.5 ? 1 : 0);
  }

  update(time, delta, desiredDirection) {
      if (time > this.phaseEnd) {
          if (this.phase == 0) {
              // Bird has been gliding
              if (desiredDirection < 0) {
                  // Wants to raise -> moving wings up
                  this.phase = 1;
              } else {
                  // Does not want to raise -> continue gliding
                  this.phase = 0;
              }
          } else if (this.phase == 1) {
              // Bird has been moving wing up from gliding
              // -> perform downward stroke
              this.phase = 2;
          } else if (this.phase == 2) {
              // Bird has made downward stroke
              if (desiredDirection < 0) {
                  // Wants to raise -> moving wing all the way up
                  this.phase = 4;
              } else {
                  // Does not want to raise -> raise wing for gliding
                  this.phase = 3;
              }
          } else if (this.phase == 3) {
              // Birds has moved wings to gliding
              // -> glide
              this.phase = 0;
          } else if (this.phase == 4) {
              // Birds has been moving winp up from downward stroke
              // -> perform downward stroke
              this.phase = 2;
          }
          var duration = this.phaseDurations[this.phase];
          this.phaseEnd = time + duration;

          var targetScale = 0;
          var targetAccelerationX = 0;
          var targetAccelerationY = 0;
          var ease = 'Sine.easeInOut';
          if (this.phase == 0) {
              targetScale = this.targetScales['glide'];
          } else if (this.phase == 1) {
              targetScale = this.targetScales['up'];
              ease = 'Cubic.easeOut';
          } else if (this.phase == 2) {
              targetScale = this.targetScales['down'];
              targetAccelerationX = this.flapAccelerationX;
              targetAccelerationY = this.flapAccelerationY;
              ease = 'Quint.easeOut';
          } else if (this.phase == 3) {
              targetScale = this.targetScales['glide'];
          } else if (this.phase == 4) {
              targetScale = this.targetScales['up'];
              ease = 'Cubic.easeOut';
          }

          this.wingAccelerationX = 0;
          this.wingAccelerationY = 0;

          targetScale *= randomBetween(0.9, 1.1);
          targetAccelerationX *= randomBetween(0.9, 1.1);
          targetAccelerationY *= randomBetween(0.9, 1.1);
          duration *= randomBetween(0.8, 1.2);
          this.bird.timeline = game.tweens.timeline({
              targets: this,
              ease: ease,
              tweens: [{
                  wingScale: targetScale,
                  wingAccelerationX: targetAccelerationX,
                  wingAccelerationY: targetAccelerationY,
                  duration: duration,
              }],
          });
      }

      var targetHeight = this.fullHeight * this.wingScale;
      // Guarding against 0 height, which kills off the sprite.
      if (Math.abs(targetHeight) < 1) {
          targetHeight = targetHeight >= 0 ? 1 : -1;
      }
      this.setDisplaySize(this.fullWidth, targetHeight);
  }
}

class Beak extends Phaser.GameObjects.Rectangle {
  constructor(bodySpec, birdWidth, birdHeight, flippedFactor, depth) {
      const x1 = (bodySpec.beak[0][0] - bodySpec.center[0]) / bodySpec.width * birdWidth;
      const y1 = (bodySpec.beak[0][1] - bodySpec.center[1]) / bodySpec.height * birdHeight;
      const x2 = (bodySpec.beak[1][0] - bodySpec.center[0]) / bodySpec.width * birdWidth;
      const y2 = (bodySpec.beak[1][1] - bodySpec.center[1]) / bodySpec.height * birdHeight;
      const xc = (x1 + x2) / 2 * flippedFactor;
      const yc = (y1 + y2) / 2;
      const width = (x2 - x1 + 1);
      const height = y2 - y1 + 1;
      super(game, xc, yc, width, height, 0x808080, 0);
      this.setOrigin(0.5, 0.5);
      this.depth = depth;
  }
}

class Bird extends Phaser.GameObjects.Container {
  constructor(flavor, width, x, y, bodySpec, minScale, maxScale, startSpeed) {
    super(game);

    const actor = this.constructor.name;
    var flavored_actor = actor + '-' + flavor;
    this.createTextures(flavored_actor, bodySpec);
    this.depth = Math.random();
    this.flipped = Math.random() > 0.5;
    this.flippedFactor = this.flipped ? -1 : 1;
    this.rotationFactor = bodySpec.rotationFactor || 1;

    var body = game.add.image(0, 0, flavored_actor + '-body');

    var scale = scaleBetween(minScale, maxScale, this.depth) * refToScreen;
    var height = body.height / body.width * width * scale;
    var width = width * scale;
    body.setOrigin((this.flipped ? bodySpec.width - bodySpec.center[0] : bodySpec.center[0]) / bodySpec.width, bodySpec.center[1] / bodySpec.height);
    body.setFlipX(this.flipped);
    body.setDisplaySize(width, height);

    this.destroyOffset = Math.sqrt(width * width + height * height);
    this.add(body);

    this.phaseBorders = [randomBetween(0.1, 0.4), randomBetween(0.6, 0.9)];
    this.phaseYRateTargets = [];
    for (var i=0; i<=this.phaseBorders.length; i++) {
        this.phaseYRateTargets.push(randomBetween(0.2, 0.8));
    }

    this.coordinateCorrectionFactor = depthCorrectionFactor(this.depth) * refToScreen;

    var wing = new Wings(0, 0, flavored_actor + '-wing', this, body, bodySpec);
    wing.setFlipX(this.flipped);
    this.add(wing);
    this.wing = wing;

    game.physics.world.enable(this);

    this.body.setGravityX(5 * this.flippedFactor);
    this.body.setGravityY(140);
    this.body.setVelocityX(-startSpeed * randomBetween(0.9, 1.1) * this.coordinateCorrectionFactor * this.flippedFactor);
    this.body.setVelocityY(randomBetween(-0.2, 0.1) * startSpeed * randomBetween(0.9, 1.1) * this.coordinateCorrectionFactor);
    this.x = this.flipped ? 0 : scanariumConfig.width;
    this.y = scanariumConfig.height * randomBetween(0.1, 0.9);

    var beak = new Beak(bodySpec, body.displayWidth, body.displayHeight, this.flippedFactor, this.depth);
    game.physics.world.enable(beak);
    beak.body.syncBounds=true;
    this.add(beak);

    groupBeaks.add(beak);
  }

  createTextures(flavored_actor, bodySpec) {
    if (!game.textures.exists(flavored_actor + '-body')) {
      this.createTexturesForce(flavored_actor, bodySpec);
    }
  }

  createTexturesForce(flavored_actor, bodySpec) {
    const full_texture = game.textures.get(flavored_actor);
    const full_texture_source_index = 0;
    const full_source = full_texture.source[full_texture_source_index];
    const full_width = full_source.width;
    const full_height = full_source.height;

    var body = game.make.renderTexture({
      width: full_width,
      height: full_height,
    }, false);
    body.draw(flavored_actor);

    var wing = game.make.renderTexture({
      width: full_width,
      height: full_height,
    }, false);
    wing.draw(flavored_actor);

    const wingEraser = game.make.graphics();
    wingEraser.fillStyle(0xffffff, 1);
    wingEraser.beginPath();
    const factorX = full_width / bodySpec.width;
    const factorY = full_height / bodySpec.height;
    const points = bodySpec.wing.shape;
    wingEraser.moveTo(points[points.length-1][0] * factorX, points[points.length-1][1] * factorY);
    points.forEach((point) => {
      wingEraser.lineTo(point[0] * factorX, point[1] * factorY);
    });
    wingEraser.closePath();
    wingEraser.fillPath();

    body.erase(wingEraser);
    body.saveTexture(flavored_actor + '-body');

    var notWingEraser = game.make.renderTexture({
      width: full_width,
      height: full_height,
    }, false);
    notWingEraser.fill(0xffffff, 1);
    notWingEraser.erase(wingEraser);

    wing.erase(notWingEraser);
    wing.saveTexture(flavored_actor + '-wing');
  }

  update(time, delta) {
    const xRate = (this.flipped ? scanariumConfig.width - this.x : this.x) / scanariumConfig.width;
    var phase = 0;
    while (phase < this.phaseBorders.length && xRate > this.phaseBorders[phase]) {
        phase++;
    }
    const targetYRate = this.phaseYRateTargets[phase];
    const yRate = this.y / scanariumConfig.height;

    var desiredDirection = 0;
    if (Math.abs(targetYRate - yRate) > 0.1) {
        desiredDirection = (targetYRate - yRate) > 0 ? 1 : -1;
    }
    this.wing.update(time, delta, desiredDirection);

    this.body.setAccelerationX(-this.wing.wingAccelerationX * this.flippedFactor);
    this.body.setAccelerationY(this.wing.wingAccelerationY);

    this.rotation = this.rotationFactor * Math.atan2(-this.body.velocity.y * this.flippedFactor, -this.body.velocity.x * this.flippedFactor);
  }
}
