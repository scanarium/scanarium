// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class ZaggedButterfly extends BackFlapCreature {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            minWidthRef: 210,
            maxWidthRef: 330,
            bodySpec: {
                points: [
                    [114, 0],
                    [178, 86],
                    [178, 155],
                    [192, 155],
                    [192, 86],
                    [248, 0],
                ],
                centerY: 79,
                width: 370,
                height: 196,
            },
            wiggleX: 4,
            wiggleY: 4,
            wiggleAngle: 10,
            minFlapCycleLength: 130,
            maxFlapCycleLength: 170,
        }));
    }
}

actorManager.registerActor(ZaggedButterfly);
