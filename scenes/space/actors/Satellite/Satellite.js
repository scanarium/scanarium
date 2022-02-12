// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class Satellite extends PlanetBase {
    constructor(parameters) {
        mergeIntoObject(parameters, {
            widthMin: 100,
            widthMax: 200,
        });
        super(parameters);
    }
}

actorManager.registerActor(Satellite);
