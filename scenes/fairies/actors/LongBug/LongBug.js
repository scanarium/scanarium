// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class LongBug extends WingWiggleCreature {
    constructor(x, y, flavor) {
        const minWidthRef = 250;
        const maxWidthRef = 350;
        const body = {
          wings: [
            {
              points: [
                [0, 138],
                [170, 132],
                [197, 130],
                [210, 128],
                [207, 134],
                [206, 140],
                [205, 159],
                [0, 240],
              ],
              axis: [205 + 25, 159],
              shift: [3, 0],
              minAngle: 2,
              maxAngle: 32,
            },
            {
              points: [
                [500, 138],
                [344, 130],
                [303, 127],
                [293, 127],
                [295, 134],
                [296, 157],
                [500, 240],
              ],
              axis: [296 - 25, 157],
              shift: [-3, 0],
              minAngle: -2,
              maxAngle: -32,
            },
          ],
          background_points: [
              [0, 0],
              [0, 130],
              [145, 130],
              [169, 133],
              [208, 130],
              [213, 125],
              [222, 124],
              [221, 122],
              [217, 116],
              [212, 102],
              [193, 0],
              [341, 0],
              [290, 106],
              [284, 115],
              [276, 123],
              [286, 123],
              [293, 127],
              [303, 127],
              [344, 130],
              [500, 134],
              [500, 0],
          ],
          centerY: 140,
          width: 500,
          height: 378,
        };
        const wiggleX = 4;
        const wiggleY = 4;
        const wiggleAngle = 2;
        const minFlapCycleLength = 130;
        const maxFlapCycleLength = 160;
        super(flavor, x, y, minWidthRef, maxWidthRef, body,
              wiggleX, wiggleY, wiggleAngle,
              minFlapCycleLength, maxFlapCycleLength);
    }
}

actorManager.registerActor(LongBug);