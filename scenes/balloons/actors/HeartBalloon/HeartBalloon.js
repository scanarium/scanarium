// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class HeartBalloon extends BaseBalloon {
    constructor(parameters) {
        mergeIntoObject(parameters, {
            width: 160,
            spec: {
                shreds : [
                    {x: 53, y: 49, r: 45},
                    {x: 160, y: 47, r: 45},
                    {x: 102, y: 136, r: 30},
                ],
                width: 210,
                height: 213,
            },
        });
        super(parameters);
    }
}

actorManager.registerActor(HeartBalloon);
