// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class PlanetWithRing extends PlanetBase {
    constructor(parameters) {
        mergeIntoObject(parameters, {
            widthMin: 107,
            widthMax: 320,
        });
        super(parameters);

        // Resetting angular velocity, as it looks off, if the planet has a
        // ring.
        this.mainSprite.body.setAngularVelocity(0);
    }
}

actorManager.registerActor(PlanetWithRing);
