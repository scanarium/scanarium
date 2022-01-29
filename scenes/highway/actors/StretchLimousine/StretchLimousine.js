// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class StretchLimousine extends Vehicle {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 400,
            initialMaxSpeed: 750,
            lengthCm: 784,
            tires: [
                {x1: 78, x2: 160, y1: 144, y2: 226, w: 1000, h: 227},
                {x1: 825, x2: 907, y1: 144, y2: 226, w: 1000, h: 227},
            ],
            undercarriage: [
                {points: [[65, 190], [918, 190], [918, 133], [65, 133]], w: 1000, h: 227},
            ],
            angularShake: 0.01,
            yShake: 0.5,
        }));
    }
}

actorManager.registerActor(StretchLimousine);
