// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class PlainBalloon extends BaseBalloon {
    constructor(parameters) {
        mergeIntoObject(parameters, {
            width: 90,
            spec: {
                shreds : [
                    {x: 72, y: 41, r: 30},
                    {x: 52, y: 122, r: 20},
                    {x: 20, y: 40, r: 10},
                ],
                width: 108,
                height: 165,
            },
        });
        super(parameters);
    }
}

actorManager.registerActor(PlainBalloon);
