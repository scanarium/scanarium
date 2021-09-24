// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class FlowerFairy extends BackFlapCreature {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            minWidthRef: 231,
            maxWidthRef: 350,
            bodySpec: {
                points: [
                    [119, 0],
                    [148, 72],
                    [140, 73],
                    [135, 74],
                    [132, 77],
                    [130, 81],
                    [128, 87],
                    [126, 94],
                    [125, 100],
                    [109, 134],
                    [90, 159],
                    [90, 263],
                    [219, 263],
                    [219, 159],
                    [191, 99],
                    [191, 93],
                    [190, 88],
                    [189, 83],
                    [187, 78],
                    [184, 74],
                    [167, 70],
                    [167, 65],
                    [209, 0],
                ],
                centerY: 80,
                width: 314,
                height: 264,
            },
            wiggleX: 1,
            wiggleY: 1,
            wiggleAngle: 2,
            minFlapCycleLength: 150,
            maxFlapCycleLength: 190,
        }));
    }
}

actorManager.registerActor(FlowerFairy);
