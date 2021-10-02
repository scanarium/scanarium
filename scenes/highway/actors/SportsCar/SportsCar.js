// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class SportsCar extends Vehicle {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 600,
            initialMaxSpeed: 1300,
            lengthCm: 470,
            tires: [
                {x1: 82, x2: 150, y1: 66, y2: 133, w: 473, h: 134},
                {x1: 366, x2: 433, y1: 66, y2: 133, w: 473, h: 134},
            ],
            undercarriage: [
                {points: [[70, 118], [420, 118], [447, 94], [429, 56], [115, 56], [70, 65]], w: 473, h: 134},
            ],
            angularShake: 0.05,
            yShake: 0.5,
        }));
    }
}

actorManager.registerActor(SportsCar);
