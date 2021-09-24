// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class Tit extends Bird {
    constructor(parameters) {
        const bodySpec = {
            wing: {
                shape: [
                    [0, 300],
                    [198, 409],
                    [450, 409],
                    [450, 0],
                    [100, 0],
                ],
                durations: {
                    glide: 100,
                    glideToUp: 50,
                    upToDown: 50,
                    downToGlide: 75,
                    downToUp: 100,
                },
                flapY: 409,
                flapAcceleration: [2000, 1000],
            },
            center: [86, 437],
            beak: [
                [0, 445],
                [142, 460],
            ],
            width: 690,
            height: 582,
        };
        mergeIntoObject(parameters, {
            width: 100,
            bodySpec: bodySpec,
            minScale: 0.4,
            maxScale: 1,
            startSpeed: 550,
        });
        super(parameters);
    }
}

actorManager.registerActor(Tit);
