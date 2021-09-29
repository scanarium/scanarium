// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class SemiTrailerBox extends SemiTrailer {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 400,
            initialMaxSpeed: 750,
            widthRef: 1700,
            tires: [
                {x1: 334, x2: 377, y1: 151, y2: 194, w: 500, h: 194},
                {x1: 385, x2: 428, y1: 151, y2: 194, w: 500, h: 194},
            ],
            undercarriage: [
                {points: [[325, 168], [440, 168], [440, 140], [325, 140]], w: 500, h: 194},
            ],
            pillar: {
                x1: 138, x2: 154, y1: 166, y2: 194,
                width: 500, height:194,
                translate: -22,
            },
            decal: {x1: 0, y1: 0, x2: 496, y2: 134, w: 500, h: 194},
            angularShake: 0.2,
            yShake: 0.5,
            tractorCouplingPoint: {x: 44, y: 134, width: 500, height: 194},
        }));
    }
}

actorManager.registerActor(SemiTrailerBox);
