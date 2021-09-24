// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class PoliceCar extends Vehicle {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 400,
            initialMaxSpeed: 750,
            widthRef: 650,
            tires: [
                {x1: 134, x2: 275, y1: 330, y2: 472, w: 1000, h: 473},
                {x1: 751, x2: 892, y1: 330, y2: 472, w: 1000, h: 473},
            ],
            undercarriage: [
                {points: [[100, 405], [920, 405], [920, 302], [110, 302]], w: 1000, h: 473},
            ],
            angularShake: 0.1,
            yShake: 1.5,
            decal: {x1: 311, y1: 239, x2: 805, y2: 318, w: 1000, h: 473},
            beacon: {x1: 504, y1: 8, x2: 586, y2: 34, w: 1000, h: 468, chance: 0.2, speedFactor: 2.5, phaseLength: 1000, phaseSlotLength: 100, litSlots: [0, 2]},
        }));
    }
}
actorManager.registerActor(PoliceCar);
