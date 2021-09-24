// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class CompactMpv extends Vehicle {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 400,
            initialMaxSpeed: 750,
            widthRef: 650,
            tires: [
                {x1: 127, x2: 263, y1: 271, y2: 407, w: 951, h: 408},
                {x1: 714, x2: 849, y1: 271, y2: 407, w: 951, h: 408},
            ],
            undercarriage: [
                {points: [[77, 344], [879, 344], [879, 240], [77, 240]], w: 951, h: 408},
            ],
            angularShake: 0.1,
            yShake: 1.5,
        }));
    }
}

actorManager.registerActor(CompactMpv);
