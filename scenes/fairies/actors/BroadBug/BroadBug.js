// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class BroadBug extends WingWiggleCreature {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            minWidthRef: 250,
            maxWidthRef: 350,
            bodySpec: {
                wings: [
                    {
                        points: [
                            [0, 80],
                            [300, 80],
                            [327, 165],
                            [326, 181],
                            [309, 188],
                            [293, 196],
                            [284, 202],
                            [276, 210],
                            [268, 221],
                            [260, 240],
                            [244, 243],
                            [171, 230],
                            [0, 226],
                        ],
                        axis: [323, 233],
                        shift: [5, 5],
                        minAngle: 2,
                        maxAngle: 17,
                        width: 868,
                        height: 690,
                    },
                    {
                        points: [
                            [610, 246],
                            [608, 232],
                            [606, 222],
                            [600, 208],
                            [595, 200],
                            [586, 192],
                            [573, 185],
                            [561, 181],
                            [545, 177],
                            [530, 126],
                            [530, 95],
                            [869, 95],
                            [869, 226],
                            [715, 226],
                        ],
                        axis: [548, 238],
                        shift: [-5, 5],
                        minAngle: -2,
                        maxAngle: -17,
                        width: 868,
                        height: 690,
                    },
                    {
                        points: [
                            [0, 226],
                            [171, 230],
                            [244, 243],
                            [260, 246],
                            [258, 280],
                            [258, 349],
                            [246, 414],
                            [0, 414],
                        ],
                        axis: [260 + 80, 300],
                        shift: [5, 0],
                        minAngle: -30,
                        maxAngle: 30,
                        width: 868,
                        height: 690,
                    },
                    {
                        points: [
                            [610, 246],
                            [715, 226],
                            [869, 226],
                            [869, 420],
                            [636, 420],
                            [604, 342],
                            [610, 290],
                        ],
                        axis: [607 - 80, 295],
                        shift: [-5, 0],
                        minAngle: 30,
                        maxAngle: -30,
                        width: 868,
                        height: 690,
                    },
                ],
                centerY: 265,
                width: 868,
                height: 690,
            },
            wiggleX: 2,
            wiggleY: 2,
            wiggleAngle: 2,
            minFlapCycleLength: 130,
            maxFlapCycleLength: 160,
        }));
    }
}

actorManager.registerActor(BroadBug);
