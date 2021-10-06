// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class SemiTruckConventionalCab extends SemiTruck {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 400,
            initialMaxSpeed: 750,
            lengthCm: 620,
            tires: [
                {x1: 62, x2: 184, y1: 433, y2: 555, w: 843, h: 556},
                {x1: 526, x2: 648, y1: 433, y2: 555, w: 843, h: 556},
                {x1: 688, x2: 810, y1: 433, y2: 555, w: 843, h: 556},
            ],
            undercarriage: [
                {points: [[30, 410], [30, 488], [829, 488], [823, 427], [817, 410], 
[717, 410], [717, 394], [707, 385], [639, 385], [639, 410]], w: 843, h: 556},
            ],
            angularShake: 0.2,
            yShake: 0.5,
            trailerCouplers: {
                'SemiTrailer': {queue: 'SemiTrailer', chance: 0.8, point: {x: 678, y: 392, width: 843, height: 556}},
            },
        }));
    }
}

actorManager.registerActor(SemiTruckConventionalCab);
