// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class SpringFairy extends BackFlapCreature {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            minWidthRef: 231,
            maxWidthRef: 350,
            bodySpec: {
                points: [
                    [187, 0],
                    [187, 74],
                    [185, 81],
                    [185, 88],
                    [188, 108],
                    [188, 115],
                    [180, 116],
                    [175, 118],
                    [171, 122],
                    [168, 127],
                    [166, 134],
                    [165, 141],
                    [166, 156],
                    [171, 178],
                    [175, 190],
                    [178, 203],
                    [165, 213],
                    [155, 221],
                    [149, 227],
                    [130, 255],
                    [130, 419],
                    [281, 419],
                    [281, 240],
                    [273, 223],
                    [268, 221],
                    [261, 213],
                    [253, 206],
                    [246, 202],
                    [249, 186],
                    [253, 171],
                    [257, 156],
                    [259, 142],
                    [259, 126],
                    [258, 121],
                    [253, 116],
                    [248, 114],
                    [241, 114],
                    [240, 107],
                    [240, 93],
                    [241, 81],
                    [241, 71],
                    [240, 66],
                    [240, 0],
                ],
                centerY: 140,
                width: 421,
                height: 420,
            },
            wiggleX: 1,
            wiggleY: 1,
            wiggleAngle: 2,
            minFlapCycleLength: 150,
            maxFlapCycleLength: 190,
        }));
    }
}

actorManager.registerActor(SpringFairy);
