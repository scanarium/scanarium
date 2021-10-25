// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

// Scene: piste

function scene_preload()
{
}

function scene_create()
{
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
        this.setTexture(flavored_actor, '__BASE');
        this.setPosition(startX, startY);
        this.setOrigin(parameters.centerOfMassX, 1);
        this.setDepth(position * 100);

        game.physics.world.enable(this);
        this.lengthCm = parameters.lengthCm;
        this.speedFactor = 20 * parameters.topSpeedKmH * randomBetween(0.75, 1) * refToScreen;

        this.unjitteredRotation=Math.atan2(-scanariumConfig.height, scanariumConfig.width);
        this.rotationJitter = parameters.rotationJitter;

        this.update(0, 0);
    }

    update(time, delta) {
        // position is 0 on the top left edge between snow and
        // horizon, and is 1 in the bottom right corner.
        const position = ((this.y + this.x * scanariumConfig.height / scanariumConfig.width) / scanariumConfig.height - 0.5) / 1.5;
        const scale = 0.4 + position; // linear is good enough. And this can go above 1 in the bottom right corner.
        const width = this.lengthCm * 2 * scale * refToScreen;
        const height = this.height * width / this.width;
        this.setSize(width, height);
        this.setDisplaySize(width, height);

        const speed= scale * this.speedFactor;
        this.body.setVelocityX(-speed*Math.cos(this.unjitteredRotation));
        this.body.setVelocityY(-speed*Math.sin(this.unjitteredRotation));

        this.rotation = this.unjitteredRotation + randomPlusMinus(this.rotationJitter);
    }
}
