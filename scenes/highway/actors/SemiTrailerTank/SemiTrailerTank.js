// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class SemiTrailerTank extends SemiTrailer {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 400,
            initialMaxSpeed: 750,
            lengthCm: 1020,
            tires: [
                {x1: 605, x2: 693, y1: 299, y2: 388, w: 1000, h: 388},
                {x1: 707, x2: 795, y1: 299, y2: 388, w: 1000, h: 388},
                {x1: 809, x2: 897, y1: 299, y2: 388, w: 1000, h: 388},
            ],
            undercarriage: [
                {points: [[580, 336], [920, 336], [920, 280], [580, 280]], w: 1000, h: 388},
            ],
            pillar: {
                x1: 138, x2: 154, y1: 166, y2: 194,
                width: 500, height:194,
                translate: -22,
            },
            decal: {x1: 17, y1: 0, x2: 962, y2: 257, w: 1000, h: 388},
            angularShake: 0.2,
            yShake: 0.5,
            tractorCouplingPoint: {x: 44, y: 268, width: 1000, height: 388},
        }));
    }
}

actorManager.registerActor(SemiTrailerTank);
