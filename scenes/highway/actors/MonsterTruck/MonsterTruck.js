// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class MonsterTruck extends Vehicle {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 500,
            initialMaxSpeed: 900,
            widthRef: 600,
            tires: [
                {x1: 1, x2: 168, y1: 101, y2: 267, w: 451, h: 268},
                {x1: 283, x2: 450, y1: 101, y2: 267, w: 451, h: 268},
            ],
            undercarriage: [
                {points: [[61, 87], [61, 116], [371, 116], [371, 87]], w: 450, h: 268},
            ],
            angularShake: 0.2,
            yShake: 3,
        }));
    }
}

actorManager.registerActor(MonsterTruck);
