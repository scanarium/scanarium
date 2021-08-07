// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class SemiTrailerBox extends Vehicle {
    constructor(x, y, flavor) {
        const initialMinSpeed = 400;
        const initialMaxSpeed = 750;
        const width = 1700;
        const tires = [
          {x1: 334, x2: 377, y1: 151, y2: 194, w: 500, h: 194},
          {x1: 385, x2: 428, y1: 151, y2: 194, w: 500, h: 194},
        ];
        const undercarriage = [
          {points: [[325, 168], [440, 168], [440, 140], [325, 140]], w: 500, h: 194},
          ];
        const angularShake = 0.2;
        const yShake = 0.5;
        super(flavor, x, y, initialMinSpeed, initialMaxSpeed, width, tires, undercarriage, angularShake, yShake);
    }
}

actorManager.registerActor(SemiTrailerBox);
