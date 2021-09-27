// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class SemiTruckCabOver extends SemiTruck {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 400,
            initialMaxSpeed: 750,
            widthRef: 750,
            tires: [
                {x1: 49, x2: 118, y1: 219, y2: 288, w: 349, h: 288},
                {x1: 261, x2: 330, y1: 219, y2: 288, w: 349, h: 288},
            ],
            undercarriage: [
                {points: [[30, 250], [341, 250], [334, 210], [275, 210], [275, 198], [268, 194], [240, 194], [240, 210], [30, 200]], w: 349, h: 288},
            ],
            angularShake: 0.2,
            yShake: 0.5,
            trailerCouplers: {
                'SemiTrailer': {queue: 'SemiTrailer', chance: 1, point: {x: 254, y: 194, width: 349, height: 288}},
            },
        }));
    }
}

actorManager.registerActor(SemiTruckCabOver);
