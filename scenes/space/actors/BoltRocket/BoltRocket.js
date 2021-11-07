// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class BoltRocket extends SpaceshipBase {
    constructor(parameters) {
        mergeIntoObject(parameters, {
            angle: 180,
            widthMin: 50,
            widthMax: 350,
        });
        super(parameters);

        var thrustScale = scaleBetween(0.08, 0.7, this.base_scale);

        this.addThruster(0.96, -0.4, 110, thrustScale * 0.2, 0.5, 0.3); // Top
        this.addThruster(1, 0.09, 180, thrustScale, 0, 1);              // Middle
        this.addThruster(0.96, 0.6, 250, thrustScale * 0.2, -0.5, 0.3); // Bottom
    }

    updateMotionPlan(time, delta) {
        // Having both left and right thruster on is counter-intuitive,
        // so we force one of the two (at random) off.
        this.thrusters[Math.random() > 0.5 ? 0 : 2].setThrust(0);
    }
}

actorManager.registerActor(BoltRocket);