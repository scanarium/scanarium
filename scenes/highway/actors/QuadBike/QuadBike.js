// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class QuadBike extends Vehicle {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 500,
            initialMaxSpeed: 900,
            lengthCm: 210,
            tires: [
                {x1: 2, x2: 62, y1: 129, y2: 189, w: 232, h: 190},
                {x1: 171, x2: 231, y1: 129, y2: 189, w: 232, h: 190},
            ],
            undercarriage: [
                {points: [[26, 115], [26, 167], [203, 167], [215, 157], [200, 110], [177, 115]], w: 232, h: 192},
            ],
            angularShake: 1,
            yShake: 1,
        }));
    }
}

actorManager.registerActor(QuadBike);
