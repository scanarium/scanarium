// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class SimpleButterfly extends BackFlapCreature {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            minWidthRef: 125,
            maxWidthRef: 200,
            bodySpec: {
                points: [
                    [50, 19],
                    [105, 113],
                    [105, 178],
                    [119, 178],
                    [119, 113],
                    [172, 19],
                ],
                centerY: 106,
                width: 223,
                height: 238,
            },
            wiggleX: 4,
            wiggleY: 4,
            wiggleAngle: 10,
            minFlapCycleLength: 180,
            maxFlapCycleLength: 220,
        }));
    }
}

actorManager.registerActor(SimpleButterfly);
