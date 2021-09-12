// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

// Scene: fairies

function scene_preload() {
}

function scene_create() {
}

function scene_update(time, delta) {
}

function getBorderPosition(defaultX, defaultY) {
  var width = scanariumConfig.width;
  var height = scanariumConfig.height;

  var x = defaultX;
  var y = defaultY;
  var position = Math.random() * (2 * width + 2 * height);
  if (position < width) {
    x = position;
  } else if (position < width + height) {
    x = width - x;
    y = position - width;
  } else if (position < 2 * width + height) {
    x = 2 * width + height - position;
    y = height - y;
  } else {
    y = 2 * width + 2 * height - position;
  }
  return [x, y];
}

class BackFlapWings extends Phaser.Physics.Arcade.Sprite {
  constructor(x, y, image_name, body, minCycleLength, maxCycleLength) {
    super(game, x, y, image_name);

    game.physics.world.enableBody(this);
    game.sys.updateList.add(this);

    this.x = body.x;
    this.y = body.y;
    this.fullWidth = body.width;
    this.fullHeight = body.height;
    this.setOrigin(body.originX, body.originY);
    this.cycleLength = randomBetween(minCycleLength, maxCycleLength);
    this.cycleOffset = randomBetween(0, this.cycleLength);
    this.angleFactor = 100 / 360 * 2 * Math.PI;
    this.update(0, 0);
  }

  update(time, delta) {
    var phase = Math.abs(((time + this.cycleOffset) % this.cycleLength) / (this.cycleLength / 2) - 1);

    // Pushing up factor 0 up to 0.001, as width 0 makes the sprite vanish from
    // the scene, even for later frames with width > 0.
    var currentWidth = tunnel(Math.sin(phase * this.angleFactor), 0.001, 1) * this.fullWidth;
    this.setSize(currentWidth, this.fullHeight);
    this.setDisplaySize(currentWidth, this.fullHeight);
  }
}

class WiggleWing extends Phaser.Physics.Arcade.Sprite {
  constructor(x, y, image_name, body, centerYPercent, minCycleLength, maxCycleLength, wing, points_width, points_height, syncToWing) {
    super(game, x, y, image_name);

    game.physics.world.enableBody(this);
    game.sys.updateList.add(this);

    this.x = body.x + ((wing.axis[0] + wing.shift[0])/points_width - 0.5) * body.width;
    this.y = body.y + ((wing.axis[1] + wing.shift[1])/points_height - centerYPercent) * body.height;
    this.fullWidth = body.width;
    this.fullHeight = body.height;
    this.setOrigin(body.originX + (wing.axis[0]/points_width - 0.5), body.originY + (wing.axis[1]/points_height - centerYPercent));
    this.cycleLength = randomBetween(minCycleLength, maxCycleLength);
    this.cycleOffset = randomBetween(0, this.cycleLength);
    this.minAngle = wing.minAngle;
    this.angleWidth = wing.maxAngle - wing.minAngle;
    this.setSize(this.fullWidth, this.fullHeight);
    this.setDisplaySize(this.fullWidth, this.fullHeight);

    if (syncToWing) {
      this.syncToWing = syncToWing;
      this.cycleLength = syncToWing.cycleLength;
      this.cycleOffset = syncToWing.cycleOffset;
    }

    this.update(0, 0);
  }

  update(time, delta) {
    var phase = 0;
    if (this.syncToWing) {
      phase = this.syncToWing.phase;
    } else {
      phase = ((time + this.cycleOffset) % this.cycleLength) / this.cycleLength;
    }
    this.phase = phase;
    phase = Math.abs(phase - 0.5) * 2;
    this.angle = phase * this.angleWidth + this.minAngle;
  }
}

class Creature extends Phaser.GameObjects.Container {
  constructor(flavor, x, y, minWidthRef, maxWidthRef, bodySpec, wiggleX, wiggleY, wiggleAngle, minFlapCycleLength, maxFlapCycleLength) {
    super(game, 0, 0);
    this.wiggleX = wiggleX / 2;
    this.wiggleY = wiggleY / 2;
    this.wiggleAngle = wiggleAngle / 2;

    const actor = this.constructor.name;
    var flavored_actor = actor + '-' + flavor;
    this.createTextures(flavored_actor, bodySpec);

    var body = game.add.image(0, 0, flavored_actor + '-body');
    var width = randomBetween(minWidthRef, maxWidthRef) * refToScreen;
    var base_scale = width / body.width;
    var height = body.height * base_scale;
    body.setOrigin(0.5, bodySpec.centerY / bodySpec.height);
    body.setSize(width, height);
    body.setDisplaySize(width, height);
    this.destroyOffset = Math.max(width, height) + 20;

    if (game.textures.exists(flavored_actor + '-background')) {
        var background = game.add.image(0, 0, flavored_actor + '-background');
        background.setOrigin(body.originX, body.originY);
        background.setSize(width, height);
        background.setDisplaySize(width, height);
        this.add(background);
    }

    var that = this;
    this.wings = [];
    this.addWings(flavored_actor, body, bodySpec, minFlapCycleLength, maxFlapCycleLength);
    this.wings.forEach(wing => that.add(wing));

    this.add(body);
    game.physics.world.enable(this);

    const startPosition = getBorderPosition(-this.destroyOffset + 10, -this.destroyOffset + 10);
    this.x = startPosition[0];
    this.y = startPosition[1];
    this.addTimeline();
  }

  addWings(flavored_actor, body, bodySpec, minFlapCycleLength, maxFlapCycleLength) {
  }

  addTimeline() {
    var tweens = [];
    var i;
    var steps = Math.random() * 4 + 3;
    var previousX = this.x;
    var width = scanariumConfig.width;
    var height = scanariumConfig.height;

    // First step is to quickly, but gradually appear at start position
    this.alpha = 0;
    tweens.push({
      duration: randomBetween(100, 200),
      alpha: 1,
    });

    while (tweens.length < steps) {
      var x = randomBetween(0.1, 0.9) * width;
      var y = randomBetween(0.1, 0.9) * height;
      tweens.push({
        x: x,
        y: y,
        duration: randomBetween(1000, 3000),
        hold: randomBetween(100, 1000),
        angle: tunnel((x-previousX) * screenToRef / 100, -15, 15),
      });
      previousX = x;
    }

    // And finally, we add a move to a position that will have the creature
    // evicted and destroyed.
    const endPosition = getBorderPosition(-this.destroyOffset - 10, -this.destroyOffset - 10);
    tweens.push({
      x: endPosition[0],
      y: endPosition[1],
      duration: randomBetween(1000, 3000),
    });

    // When having a destroy position with positive X and Y coordinates, it
    // might be that a window resize made the destroy position a proper
    // position. So we back up with making one coordinate negative. This kills
    // the sprite for good (regargless of window resizes).
    tweens.push({
      x: endPosition[0],
      y: -this.destroyOffset - 10,
      duration: randomBetween(1000, 3000),
    });

    this.timeline = game.tweens.timeline({
      targets: this,
      ease: 'Cubic.easeOut',
      tweens: tweens,
    });
  }

  createTextures(flavored_actor, bodySpec) {
    if (!game.textures.exists(flavored_actor + '-body')) {
      this.createTexturesForce(flavored_actor, bodySpec);
    }
  }

  createTexturesForce(flavored_actor, bodySpec) {
    var body = renderTextureFromTexture(flavored_actor);
    body.saveTexture(flavored_actor + '-body');
  }

  update(time, delta) {
    this.x += randomBetween(-this.wiggleX, this.wiggleX) * refToScreen;
    this.y += randomBetween(-this.wiggleY, this.wiggleY) * refToScreen;
    this.angle += randomBetween(-this.wiggleAngle, this.wiggleAngle);
    this.wings.forEach(wing => wing.update(time, delta));
  }
}

class BackFlapCreature extends Creature {
  addWings(flavored_actor, body, bodySpec, minFlapCycleLength, maxFlapCycleLength) {
    var wings = new BackFlapWings(0, 0, flavored_actor + '-wings', body, minFlapCycleLength, maxFlapCycleLength);
    this.wings.push(wings);
  }

  createTexturesForce(flavored_actor, bodySpec) {
    const full_texture = game.textures.get(flavored_actor);
    const full_texture_source_index = 0;
    const full_source = full_texture.source[full_texture_source_index];
    const full_width = full_source.width;
    const full_height = full_source.height;

    var wings = renderTextureFromTexture(flavored_actor);

    const bodyEraser = game.make.graphics();
    bodyEraser.fillStyle(0xffffff, 1);
    bodyEraser.beginPath();
    const factorX = full_width / bodySpec.width;
    const factorY = full_height / bodySpec.height;
    const points = bodySpec.points;
    bodyEraser.moveTo(points[points.length-1][0] * factorX, points[points.length-1][1] * factorY);
    points.forEach((point) => {
      bodyEraser.lineTo(point[0] * factorX, point[1] * factorY);
    });
    bodyEraser.closePath();
    bodyEraser.fillPath();
    wings.erase(bodyEraser);
    wings.saveTexture(flavored_actor + '-wings');

    var body = renderTextureFromTexture(flavored_actor);

    var eraser = game.make.renderTexture({
      width: full_width,
      height: full_height,
    }, false);
    eraser.fill(0xffffff, 1);
    eraser.erase(bodyEraser);

    body.erase(eraser);
    body.saveTexture(flavored_actor + '-body');
  }
}

class WingWiggleCreature extends Creature {
  addWings(flavored_actor, body, bodySpec, minFlapCycleLength, maxFlapCycleLength) {
    var last_wing = null;
    bodySpec.wings.forEach((wing, i) => {
        var wing = new WiggleWing(0, 0, flavored_actor + '-wing-' + i, body, bodySpec.centerY / bodySpec.height, minFlapCycleLength, maxFlapCycleLength, wing, bodySpec.width, bodySpec.height, last_wing);
        this.wings.push(wing);

        last_wing = wing;
    });
  }

  extractTexture(flavored_actor, name, points, points_width, points_height, full_width, full_height, background) {
    const extractionMask = game.make.graphics();
    extractionMask.fillStyle(0xffffff, 1);
    extractionMask.beginPath();
    const factorX = full_width / points_width;
    const factorY = full_height / points_height;
    extractionMask.moveTo(points[points.length-1][0] * factorX, points[points.length-1][1] * factorY);
    points.forEach((point) => {
      extractionMask.lineTo(point[0] * factorX, point[1] * factorY);
    });
    extractionMask.closePath();
    extractionMask.fillPath();

    if (background) {
      background.erase(extractionMask);
    }

    var invertedExtractionMask = game.make.renderTexture({
      width: full_width,
      height: full_height,
    }, false);
    invertedExtractionMask.fill(0xffffff, 1);
    invertedExtractionMask.erase(extractionMask);

    var extracted = renderTextureFromTexture(flavored_actor);
    extracted.erase(invertedExtractionMask);

    extracted.saveTexture(flavored_actor + '-' + name);
  }

  createTexturesForce(flavored_actor, bodySpec) {
    const full_texture = game.textures.get(flavored_actor);
    const full_texture_source_index = 0;
    const full_source = full_texture.source[full_texture_source_index];
    const full_width = full_source.width;
    const full_height = full_source.height;

    var body = renderTextureFromTexture(flavored_actor);

    var that = this;
    bodySpec.wings.forEach((wing, i) => {
        that.extractTexture(flavored_actor, 'wing-' + i, wing.points, bodySpec.width, bodySpec.height, full_width, full_height, body);
    });

    that.extractTexture(flavored_actor, 'background', bodySpec.background_points, bodySpec.width, bodySpec.height, full_width, full_height, body);

    body.saveTexture(flavored_actor + '-body');
  }
}
