// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class WoodFairy extends BackFlapCreature {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            minWidthRef: 154,
            maxWidthRef: 231,
            bodySpec: {
                points: [
                    [104, 0],
                    [114, 50],
                    [112, 59],
                    [111, 67],
                    [111, 78],
                    [112, 82],
                    [105, 93],
                    [101, 101],
                    [98, 109],
                    [97, 116],
                    [97, 126],
                    [95, 130],
                    [95, 261],
                    [193, 261],
                    [193, 126],
                    [194, 119],
                    [194, 102],
                    [192, 93],
                    [189, 84],
                    [186, 76],
                    [190, 65],
                    [195, 52],
                    [197, 46],
                    [198, 40],
                    [226, 0],
                ],
                centerY: 55,
                width: 296,
                height: 262,
            },
            wiggleX: 1,
            wiggleY: 1,
            wiggleAngle: 2,
            minFlapCycleLength: 120,
            maxFlapCycleLength: 150,
        }));
    }
}

actorManager.registerActor(WoodFairy);
