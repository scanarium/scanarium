// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

// Scene: piste

var riders = [];
var slopeRotation; // radian

var screenWidth;
var screenHeight;

const maxSlopeDeviation = 0.2; // radian

var drawableBackground;
var skids;
const SKID_WIDTH = 16;
const SKID_HEIGHT = 16;

function scene_preload()
{
  skids = game.load.image('skids', scene_dir + '/skids.png');
}

function riderCollision(rider1, rider2) {
    var evadeDirection = 1;
    if (rider1.depth > rider2.depth) {
        evadeDirection = -1;
    }
    rider1.unjitteredRotation += evadeDirection * rider1.speedFactor / 200000;
    rider2.unjitteredRotation -= evadeDirection * rider2.speedFactor / 200000;
}

function scene_create()
{
    drawableBackground = createRenderTextureFromTexture('background');
    game.textures.get('background').destroy();
    drawableBackground.saveTexture('background');
    background.setTexture('background', '__BASE');

    skidTexture = game.textures.get('skids');
    for (var j=0; j < skidTexture.source[0].height / SKID_HEIGHT; j++) {
        for (var i=0; i < skidTexture.source[0].width / SKID_WIDTH; i++) {
            var frameName = 'skid-' + (j ? 'dark' : 'light') + '-' + i;
            skidTexture.add(frameName, 0, i * SKID_WIDTH, j * SKID_HEIGHT, SKID_WIDTH, SKID_HEIGHT);
        }
    }
    riders = game.add.group();
    game.physics.add.overlap(riders, riders, riderCollision);
}

function scene_update(time, delta) {
    drawableBackground.beginDraw();
    actorManager.actors.forEach(actor => {
        //const last = parameters.lastUnjitteredRotation;
        const skid = 'skid-' + (actor.isTurning ? 'dark' : 'light') + '-' + chooseInt(0, 3);
        drawableBackground.batchDrawFrame('skids', skid, actor.x / screenWidth * refWidth - SKID_WIDTH / 2, actor.y / screenHeight * refHeight - SKID_WIDTH / 2);
        actor.isColliding = false;
    });
    drawableBackground.endDraw();
}

function relayout(width, height) {
  slopeRotation = Math.atan2(-height, width);
  actorManager.actors.forEach(actor => {
      const x = screenWidth ? (actor.x / screenWidth * width) : actor.x;
      const y = screenHeight ? (actor.y / screenHeight * height) : actor.y;
      actor.setPosition(x, y);
  });
  screenWidth = width;
  screenHeight = height;
};
LayoutManager.register(relayout);

class Rider extends Phaser.Physics.Arcade.Sprite {
    /* parameters has the following key/values:
       flavor - actor's flavor
       x - desired initial x position
       y - desired initial y position
       lengthCm - The actor's reference length in cm
       topSpeedKmH- The actor's top speed in km/h
       rotationJitter - The jitter around the general rotation
       centerOfMassX - Value between 0 and 1. 0 center of mass is on the left. 1 center of mass is on the right
    */
    constructor(parameters) {
        super(game);

        const actor = this.constructor.name;
        const flavored_actor = actor + '-' + parameters.flavor;
        const position = Math.random();
        var startX = screenWidth * (position < 0.7 ? 0.5 + position / 0.7 / 2 : 1);
        var startY = screenHeight * (position < 0.7 ? 0 : position - 0.7);
        this.centerOfMassX = parameters.centerOfMassX;
        this.setTexture(flavored_actor, '__BASE');
        this.setPosition(startX, startY);
        this.setOrigin(this.centerOfMassX, 1);
        this.originalWidth = this.width;
        this.originalHeight = this.height;

        game.physics.world.enable(this);
        this.lengthCm = parameters.lengthCm;
        this.speedFactor = 20 * parameters.topSpeedKmH * randomBetween(0.75, 1);

        this.unjitteredRotation = slopeRotation;
        this.lastUnjitteredRotation = this.unjitteredRotation;
        this.rotationJitter = parameters.rotationJitter;

        this.update(0, 0);

        // Shift back the actor until it is no longer on-screen, to give smooth start
        startX += this.displayWidth * Math.cos(this.unjitteredRotation) * this.centerOfMassX;
        startY += this.displayHeight * Math.sin(this.unjitteredRotation) * this.centerOfMassX;
        this.setPosition(startX, startY);

        riders.add(this);
    }

    update(time, delta)  {
        // position is 0 on the top left edge between snow and
        // horizon, and is 1 in the bottom right corner.
        const position = tunnel(((this.y + this.x * screenHeight / screenWidth) / screenHeight - 0.5) / 1.5, 0, 1);
        const scale = 0.4 + position; // linear is good enough. And this can go above 1 in the bottom right corner.
        const oWidth = this.originalWidth;
        const oHeight = this.originalHeight;
        const width = this.lengthCm * 2 * scale * refToScreen;
        const pixelScale = width / oWidth;
        const height = oHeight * pixelScale;
        this.setDisplaySize(width, height);
        this.setSize(oWidth * 1.5, oWidth * 1.5, false);
        this.setOffset(oWidth * (this.centerOfMassX - 1), oHeight - oWidth / 2);
        this.setDepth(position * 100);

        const speed= scale * this.speedFactor * refToScreen;

        const minRotation = slopeRotation - maxSlopeDeviation;
        const maxRotation = slopeRotation + maxSlopeDeviation * Math.min(1, position * 10 - 0.3);
        this.unjitteredRotation = tunnel(this.unjitteredRotation, minRotation, maxRotation);
        this.body.setVelocityX(-speed*Math.cos(this.unjitteredRotation));
        this.body.setVelocityY(-speed*Math.sin(this.unjitteredRotation));

        this.rotation = this.unjitteredRotation + randomPlusMinus(this.rotationJitter);
        this.isTurning = (this.lastUnjitteredRotation != this.unjitteredRotation);
        if (this.isTurning) {
            this.lastUnjitteredRotation = this.unjitteredRotation;
        }
    }
}
