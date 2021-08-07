// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class FlyingSaucer extends SpaceshipBase {
    constructor(x, y, flavor) {
        var lengthMin = 50;
        var lengthMax = 350;

        super(flavor, x, y, 90, lengthMin, lengthMax);

        var thrustScale = scaleBetween(0.06, 0.4, this.base_scale);

        this.addThruster(-0.75, 0.85, -72, thrustScale, 1, 0.2);   // Left
        this.addThruster(-0.25, 0.99, -87, thrustScale, 0.2, 0.7); // Middle-Left
        this.addThruster(0.25, 0.99, -96, thrustScale, -0.2, 0.7); // Middle-Right
        this.addThruster(0.75, 0.85, -108, thrustScale, -1, 0.2);  // Right
    }
}

actorManager.registerActor(FlyingSaucer);
