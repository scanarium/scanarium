// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class ActorManagerConfigLoader {
    constructor(actorManager, initDoneCallback) {
        this.actorManager = actorManager;
        this.configFetches = 0;
        this.actors_config = null;
        this.actors_latest_config = null;
        this.initDoneCallback = initDoneCallback;
    }

    reload() {
        // If we did not check on loading being blocked, the config reload
        // requests would get queued up and once loading is allowed again,
        // we'd get 100s of requests to reload the same file. As this only
        // hurts the whole situation, we simlpy skip reloading during the
        // block. We'll catch up after the block automatically.
        if (!isLoadingBlocked()) {
            this.forceReload();
        }
    }

    isConfigLoaded() {
        return this.actors_config != null && this.actors_latest_config != null;
    }

    forceReload() {
        var that = this;
        var load = function (url, callback) {
            loadDynamicConfig(dyn_scene_dir + '/' + url, function(payload) {
                var wasLoaded = that.isConfigLoaded();

                callback(payload);

                if (!wasLoaded) {
                    if (that.isConfigLoaded() && that.initDoneCallback) {
                        that.initDoneCallback();
                        that.initDoneCallback = null;
                    }
                }
            });
        };

        load('actors-latest.json', function(payload) {
            that.actors_latest_config = payload;
        });

        if ((that.configFetches % 10) == 0) {
            load('actors.json', function(payload) {
                that.actors_config = payload;
            });
        }

        this.configFetches++;
    }
}
