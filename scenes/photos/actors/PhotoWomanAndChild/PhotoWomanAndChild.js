// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class PhotoWomanAndChild extends Photo {
    constructor(x, y, flavor) {
        const widthMm = 100; // mm
        super(flavor, x, y, widthMm);
    }
}

ActorManager.registerActor(PhotoWomanAndChild);
