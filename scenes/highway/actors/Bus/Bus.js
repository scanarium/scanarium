// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class Bus extends Vehicle {
    constructor(parameters) {
        super(mergeIntoObject(parameters, {
            initialMinSpeed: 400,
            initialMaxSpeed: 750,
            widthRef: 1000,
            tires: [
                {x1: 73, x2: 116, y1: 116, y2: 159, w: 460, h: 160},
                {x1: 347, x2: 390, y1: 116, y2: 159, w: 460, h: 160},
            ],
            undercarriage: [
                {points: [[60, 144], [410, 144], [410, 100], [60, 100]], w: 460, h: 160},
            ],
            angularShake: 0.1,
            yShake: 1.5,
        }));
    }
}

actorManager.registerActor(Bus);
