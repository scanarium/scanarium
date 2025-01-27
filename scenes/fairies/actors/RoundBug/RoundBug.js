// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class RoundBug extends BackFlapCreature {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            minWidthRef: 200,
            maxWidthRef: 300,
            bodySpec: {
                points: [
                    [133, 0],
                    [167, 91],
                    [168, 96],
                    [171, 101],
                    [174, 104],
                    [176, 107],
                    [169, 114],
                    [163, 123],
                    [158, 132],
                    [154, 143],
                    [142, 183],
                    [116, 297],
                    [310, 297],
                    [288, 196],
                    [288, 151],
                    [286, 143],
                    [284, 134],
                    [281, 127],
                    [275, 116],
                    [269, 108],
                    [258, 97],
                    [260, 93],
                    [269, 69],
                    [300, 0],
                ],
                centerY: 216,
                width: 432,
                height: 297,
            },
            wiggleX: 4,
            wiggleY: 4,
            wiggleAngle: 2,
            minFlapCycleLength: 130,
            maxFlapCycleLength: 160,
        }));
    }
}

actorManager.registerActor(RoundBug);
