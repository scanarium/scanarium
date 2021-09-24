// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class WaterElf extends BackFlapCreature {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            minWidthRef: 231,
            maxWidthRef: 350,
            bodySpec: {
                points: [
                    [109, 0],
                    [161, 65],
                    [155, 66],
                    [151, 69],
                    [149, 72],
                    [147, 79],
                    [145, 87],
                    [142, 92],
                    [126, 109],
                    [126, 265],
                    [202, 265],
                    [202, 100],
                    [193, 90],
                    [191, 79],
                    [190, 72],
                    [189, 70],
                    [187, 68],
                    [184, 66],
                    [174, 63],
                    [212, 0],
                ],
                centerY: 74,
                width: 334,
                height: 265,
            },
            wiggleX: 1,
            wiggleY: 1,
            wiggleAngle: 2,
            minFlapCycleLength: 150,
            maxFlapCycleLength: 190,
        }));
    }
}

actorManager.registerActor(WaterElf);
