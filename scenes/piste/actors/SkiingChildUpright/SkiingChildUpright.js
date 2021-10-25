// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class SkiingChildUpright extends Rider {
    constructor(parameters) {
        mergeIntoObject(parameters, {
            lengthCm: 120,
            topSpeedKmH: 30,
            rotationJitter: 0.001,
            centerOfMassX: 0.6,
        });
        super(parameters);
    }
}

actorManager.registerActor(SkiingChildUpright);
