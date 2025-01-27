// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

// Scene: photos

function scene_preload()
{
    game.load.spritesheet('strips', scene_dir + '/strips.png', {frameWidth: 80, frameHeight: 240});
}

function scene_create()
{
}

function scene_update(time, delta) {
}

const STRIP_KINDS=5;
const STRIP_OVERLAYS=4;

var BLOCK_Y_START=0;
var BLOCK_Y_END=0;

class Photo extends Phaser.GameObjects.Container {
    /* parameters has the following key/values:
       flavor - actor's flavor
       x - desired initial x position
       y - desired initial y position
       widthMm - The actor's reference width in mm
    */
    constructor(parameters) {
        super(game, parameters.x, parameters.y);

        const actor = this.constructor.name;
        const texture_name = actor + '-' + parameters.flavor;

        var photo = game.add.image(0, 0, texture_name);
        const photo_unscaled_width = photo.width;
        const photo_unscaled_height = photo.height;
        const width = parameters.widthMm * 1.8 * refToScreen;
        const height = photo_unscaled_height / photo_unscaled_width * width;

        photo.setOrigin(0.5, 0.5);
        photo.setSize(width, height);
        photo.setDisplaySize(width, height);

        this.photo = photo;
        this.add(photo);

        this.addStrips(parameters.widthMm < 60);

        this.setPosition(scanariumConfig.width + width / 2 * 1.2, this.computeY(height));
        this.depth = -this.y;
        this.angle = randomBetween(-10, 10);
        this.destroyOffset = 2*width;
        this.willFall = Math.random() < (1/30);
        this.fallX = Math.random() * scanariumConfig.width * 3 / 4;

        game.physics.world.enableBody(this);

        this.body.setVelocityX(-30);
    }

    computeY(height) {
        var y = BLOCK_Y_START;
        for (var loop = 0;
             loop < 5 && y + height >= BLOCK_Y_START && BLOCK_Y_END >= y;
             loop++) {
            y = randomBetween(0, scanariumConfig.height - height) + height / 2;
        }
        BLOCK_Y_START = y + 10 * 1.8 * refToScreen; // Inset by 10 mm to allow a bit of overlay.
        BLOCK_Y_END = y + height - 10 * 1.8 * refToScreen; // Inset by 10 mm to allow a bit of overlay.
        return y;
    }

    getStripDefinition() {
        return {
            overlay: chooseInt(0, STRIP_OVERLAYS - 1),
            alpha: randomBetween(0.5, 1),
            colors: [Math.random()*0xffffff, Math.random()*0xffffff],
        }
    }

    addStrip(relX, relY, angle) {
        var stripDefinition = this.stripDefinition;
        var stripNr = chooseInt(0, STRIP_KINDS - 1);
        var strip = game.add.image(0, 0, 'strips', stripNr);
        const unscaled_width = strip.width;
        const width = 15 * 1.8 * refToScreen;
        const height = strip.height / strip.width * width;
        const x = relX * this.photo.width;
        const y = relY * this.photo.height
        const flipX = (Math.random() < 0.5);
        const flipY = (Math.random() < 0.5);
        angle += randomBetween(-10, 10)
            + (Math.random() < 0.99 ? 0 : 90) // Accidentally misaligned tape
            + (Math.random() < 0.5 ? 0 : 180) // Add half rotation to make tapes lok more divers.
        var that = this;
        var strips = [strip];
        if (stripDefinition.overlay > 0) {
            strips.push(game.add.image(0, 0, 'strips', stripNr + stripDefinition.overlay*STRIP_KINDS));
        }
        strips.forEach((sprite, index) => {
            sprite.setSize(width, height);
            sprite.setDisplaySize(width, height);
            sprite.setPosition(x, y);
            sprite.setFlipX(flipX);
            sprite.setFlipY(flipY);
            sprite.setTint(stripDefinition.colors[index]);
            sprite.angle = angle;
            sprite.alpha = stripDefinition.alpha;
            that.add(sprite);
        });
    }

    addStrips(small) {
        this.stripDefinition = this.getStripDefinition();
        const stripVariant = small ? 0 : chooseInt(0, 3);
        switch (stripVariant) {
        case 0:
            // Only top side
            this.addStrip(0, -0.5, 90);
            break;
        case 1:
            // Top side and lower corners
            this.addStrip(0, -0.5, 90);
            this.addStrip(-0.5, 0.5, -45);
            this.addStrip(0.5, 0.5, 45);
            break;
        case 2:
            // All four corners
            this.addStrip(-0.5, -0.5, 45);
            this.addStrip(-0.5, 0.5, -45);
            this.addStrip(0.5, -0.5, -45);
            this.addStrip(0.5, 0.5, 45);
            break;
        case 3:
            // Top corners and bottom side
            this.addStrip(-0.5, -0.5, 45);
            this.addStrip(0.5, -0.5, -45);
            this.addStrip(0, 0.5, 90);
            break;
        }
    }

    update() {
        if (this.willFall && this.x < this.fallX) {
            this.willFall = false;
            this.body.setVelocityY(200);
            this.body.setGravityY(2000);
            this.body.setAngularAcceleration(500 * (Math.random() > 0.5 ? 1 : -1));
        }
    }
}
