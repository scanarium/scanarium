// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class Star extends SpaceshipBase {
  constructor(parameters) {
    mergeIntoObject(parameters, {
      angle: 90,
      widthMin: 50,
      widthMax: 200,
    });
    super(parameters);

    this.body.setVelocityX(0);
    this.body.setVelocityY(0);
    sendToBack(this);

    this.angVelocity = (Math.random() > 0.8) ? randomBetween(-50, 50) : 0;
    this.addTimeline();
  }

  addTimeline() {
    var tweens = [];

    this.alpha = 0;

    // Gradually become visible
    tweens.push({
      alpha: 1,
      duration: randomBetween(1000, 3000),
      hold: randomBetween(10000, 20000),
    });

    // Gradually vanish again
    tweens.push({
      alpha: 0,
      duration: randomBetween(1000, 4000),
    });

    // Move beyond destroyOffset to get cleaned up
    tweens.push({
      x: -this.destroyOffset - 10,
      y: -this.destroyOffset - 10,
      duration: randomBetween(1000, 4000),
    });

    this.timeline = game.tweens.timeline({
      targets: this,
      ease: 'Cubic.easeInOut',
      tweens: tweens,
    });
  }

  update(time, delta) {
    super.update(time, delta);
    this.body.setAngularVelocity(this.angVelocity);
  }
}

actorManager.registerActor(Star);
