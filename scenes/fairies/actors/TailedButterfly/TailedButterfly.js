// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class TailedButterfly extends BackFlapCreature {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            minWidthRef: 210,
            maxWidthRef: 330,
            bodySpec: {
                points: [
                    [101, 0],
                    [159, 83],
                    [159, 155],
                    [174, 155],
                    [174, 83],
                    [234, 0],
                ],
                centerY: 79,
                width: 334,
                height: 225,
            },
            wiggleX: 4,
            wiggleY: 4,
            wiggleAngle: 10,
            minFlapCycleLength: 180,
            maxFlapCycleLength: 220,
        }));
    }
}

actorManager.registerActor(TailedButterfly);
