// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class SubcompactCar extends Vehicle {
    constructor(x, y, flavor) {
        const initialMinSpeed = 400;
        const initialMaxSpeed = 750;
        const width = 550;
        const tires = [
          {x1: 64, x2: 148, y1: 154, y2: 238, w: 500, h: 239},
          {x1: 371, x2: 455, y1: 154, y2: 238, w: 500, h: 239},
        ];
        const undercarriage = [
          {points: [[40, 202], [475, 202], [475, 140], [40, 140]], w: 500, h: 239},
          ];
        const angularShake = 0.1;
        const yShake = 1.5;
        super(flavor, x, y, initialMinSpeed, initialMaxSpeed, width, tires, undercarriage, angularShake, yShake);
    }
}

ScActorManager.registerActor(SubcompactCar);
