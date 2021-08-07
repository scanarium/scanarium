// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class SemiTruckCabOver extends Vehicle {
    constructor(x, y, flavor) {
        const initialMinSpeed = 400;
        const initialMaxSpeed = 750;
        const width = 750;
        const tires = [
          {x1: 49, x2: 118, y1: 219, y2: 288, w: 349, h: 288},
          {x1: 261, x2: 330, y1: 219, y2: 288, w: 349, h: 288},
        ];
        const undercarriage = [
          {points: [[30, 250], [341, 250], [334, 210], [275, 210], [275, 198], [268, 194], [240, 194], [240, 210], [30, 200]], w: 349, h: 288},
          ];
        const angularShake = 0.2;
        const yShake = 0.5;
        super(flavor, x, y, initialMinSpeed, initialMaxSpeed, width, tires, undercarriage, angularShake, yShake);
    }
}

ActorManager.registerActor(SemiTruckCabOver);
