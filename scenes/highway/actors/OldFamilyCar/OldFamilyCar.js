// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class OldFamilyCar extends Vehicle {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 300,
            initialMaxSpeed: 600,
            widthRef: 500,
            tires: [
                {x1: 46, x2: 104, y1: 92, y2: 150, w: 398, h: 151},
                {x1: 285, x2: 343, y1: 92, y2: 150, w: 398, h: 151},
            ],
            undercarriage: [
                {points: [[38, 112], [359, 112], [359, 82], [38, 82]], w: 400, h: 150},
            ],
            angularShake: 0.2,
            yShake: 1.5,
        }));
    }
}

actorManager.registerActor(OldFamilyCar);
