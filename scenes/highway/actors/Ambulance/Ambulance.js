// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class Ambulance extends Vehicle {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 400,
            initialMaxSpeed: 750,
            widthRef: 750,
            tires: [
                {x1: 94, x2: 224, y1: 407, y2: 537, w: 927, h: 539},
                {x1: 716, x2: 846, y1: 407, y2: 537, w: 927, h: 539},
            ],
            undercarriage: [
                {points: [[50, 480], [890, 480], [890, 380], [50, 380]], w: 927, h: 539},
            ],
            angularShake: 0.1,
            yShake: 1.5,
            decal: undefined,
            beacon: {x1: 340, y1: 38, x2: 365, y2: 39, w: 927, h: 539, chance: 0.25, speedFactor: 2.5, phaseLength: 400, phaseSlotLength: 100, litSlots: [0, 2], scale: 2},
        }));
    }
}

actorManager.registerActor(Ambulance);
