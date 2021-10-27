// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

// Scene: piste

var riders = [];
var slopeRotation = Math.atan2(-scanariumConfig.height, scanariumConfig.width); // radian
const maxSlopeDeviation = 0.15; // radian
const evadeSpeed = 0.005; // radian / frame

function scene_preload()
{
}

function riderCollision(rider1, rider2) {
    var evadeDirection = 1
    if (rider1.depth > rider2.depth) {
        evadeDirection = -1;
    }
    rider1.unjitteredRotation += evadeDirection * evadeSpeed;
    rider2.unjitteredRotation -= evadeDirection * evadeSpeed;
}

function scene_create()
{
    riders = game.add.group();
    game.physics.add.overlap(riders, riders, riderCollision);
}

function scene_update(time, delta) {
}

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
        const startX = scanariumConfig.width * (position < 0.7 ? 0.5 + position / 0.7 / 2 : 1);
        const startY = scanariumConfig.height * (position < 0.7 ? 0 : position - 0.7);
        const targetX = scanariumConfig.width * (position < 0.5 ? 0 : position - 0.5);
        const targetY = scanariumConfig.height * (position < 0.5 ? 0.5 + position : 1);
        this.centerOfMassX = parameters.centerOfMassX;
        this.setTexture(flavored_actor, '__BASE');
        this.setPosition(startX, startY);
        this.setOrigin(this.centerOfMassX, 1);
        this.originalWidth = this.width;
        this.originalHeight = this.height;

        game.physics.world.enable(this);
        this.lengthCm = parameters.lengthCm;
        this.speedFactor = 20 * parameters.topSpeedKmH * randomBetween(0.75, 1) * refToScreen;

        this.unjitteredRotation = slopeRotation;
        this.rotationJitter = parameters.rotationJitter;

        this.update(0, 0);
        riders.add(this);
    }

    update(time, delta)  {
        // position is 0 on the top left edge between snow and
        // horizon, and is 1 in the bottom right corner.
        const position = ((this.y + this.x * scanariumConfig.height / scanariumConfig.width) / scanariumConfig.height - 0.5) / 1.5;
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

        const speed= scale * this.speedFactor;

        const minRotation = slopeRotation - maxSlopeDeviation;
        const maxRotation = slopeRotation + maxSlopeDeviation * Math.min(1, position * 10) - 0.1;
        this.unjitteredRotation = tunnel(this.unjitteredRotation, minRotation, maxRotation);
        this.body.setVelocityX(-speed*Math.cos(this.unjitteredRotation));
        this.body.setVelocityY(-speed*Math.sin(this.unjitteredRotation));

        this.rotation = this.unjitteredRotation + randomPlusMinus(this.rotationJitter);
    }
}
