// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class Truck extends Vehicle {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 400,
            initialMaxSpeed: 750,
            lengthCm: 720,
            tires: [
                {x1: 42, x2: 94, y1: 182, y2: 233, w: 474, h: 234},
                {x1: 291, x2: 343, y1: 182, y2: 233, w: 474, h: 234},
                {x1: 358, x2: 410, y1: 182, y2: 233, w: 474, h: 234},
            ],
            undercarriage: [
                {points: [[24, 206], [420, 206], [420, 164], [24, 164]], w: 474, h: 234},
            ],
            decal: {x1: 191, y1: 0, x2: 990, y2: 370, w: 1000, h: 499},
            angularShake: 0.2,
            yShake: 1.5,
        }));
    }
}

actorManager.registerActor(Truck);
