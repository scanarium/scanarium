// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class ActorManagerActorCreator {
    constructor(actorManager, configLoader, statsTracker) {
        this.actorManager = actorManager;
        this.configLoader = configLoader;
        this.statsTracker = statsTracker;
        this.registeredActors = {};
        this.triedActors = {};
        this.loadedActorJavascripts = [];
        this.loadedActorFlavors = {};
    }

    registerActor(clazz) {
        this.registeredActors[clazz.name] = clazz;
    }


    addActorIfFullyLoaded(actor, flavor) {
        if (!(this.loadedActorJavascripts.includes(actor))) {
            // JavaScript for actor not yet fully loaded.
            return;
        }
        if (!(this.loadedActorFlavors[actor].includes(flavor))) {
            // Flavor image for actor not yet fully loaded.
            return;
        }

        // Everything's fully loaded, so we're creating and adding the actor
        this.addFullyLoadedActor(actor, flavor);
    }

    addFullyLoadedActor(actor, flavor) {
        var x = scanariumConfig.width * (Math.random() * 0.6 + 0.2);
        var y = scanariumConfig.height * (Math.random() * 0.6 + 0.2);

        var actorName = actor;
        var actor = new this.registeredActors[actor](x, y, flavor);
        if (typeof actor.destroyOffset == 'undefined') {
            actor.destroyOffset = Math.sqrt(actor.displayWidth * actor.displayWidth + actor.displayHeight * actor.displayHeight);
        }
        actor.actorName = actorName;
        actor.actorFlavor = flavor;
        game.add.existing(actor);
        this.statsTracker.trackCreation();
        this.actorManager.actors.push(actor);
        return actor;
    }

    getNewActorNameWithFlavorFromConfig(config, forceUntried) {
        // We iterate over all entries in actors_latest_config.
        // If we find one that we have not tried yet, we try it.
        // If we have already tried all, we pick a random one.
        var samples = [];
        var allProper = [];
        var untriedProper = [];
        var untriedFirstsProper = [];
        var names = Object.keys(config != null ? config['actors'] : []);
        var i;
        for (i=0; i < names.length; i++) {
            var flavors = config['actors'][names[i]];
            var j;
            for (j=0; j < flavors.length; j++) {
                const flavor = flavors[j];
                var actorSpec = [names[i], flavor];
                if (flavor == "sample") {
                    samples.push(actorSpec);
                } else {
                    var hasBeenTried = false;
                    if (names[i] in this.triedActors) {
                        hasBeenTried = this.triedActors[names[i]].includes(flavors[j]);
                    }
                    if (!hasBeenTried) {
                        untriedProper.push(actorSpec);
                        if (j == 0) {
                            untriedFirstsProper.push(actorSpec);
                        }
                    }
                    allProper.push(actorSpec);
                }
            }
        }
        var candidates = [];
        [untriedFirstsProper, (forceUntried ? untriedProper : []), allProper, samples].forEach(actors => {
            if (!candidates.length) {
                candidates = actors;
            }
        });
        return candidates.length ? candidates[Math.min(Math.floor(Math.random() * candidates.length), candidates.length - 1)] : null;
    }

    getNewActorNameWithFlavor() {
        var config = this.configLoader.actors_latest_config;
        var forceUntried = true;
        if (Math.random() < 0.3) {
            config = this.configLoader.actors_config;
            forceUntried = false;
        }
        return this.getNewActorNameWithFlavorFromConfig(config, forceUntried);
    }

    addActorRandom() {
        var actor_spec = this.getNewActorNameWithFlavor();
        if (actor_spec === null) {
            // Configs currently do not provide good actor configs
            return;
        }

        var actor_name = actor_spec[0];
        var flavor = actor_spec[1];
        this.addActor(actor_name, flavor);
    }

    addActor(actor_name, flavor) {
        var flavored_actor_name = actor_name + '-' + flavor;

        var triedActors = this.triedActors;
        if (!(actor_name in triedActors)) {
            triedActors[actor_name] = []
        }
        if (!(triedActors[actor_name].includes(flavor))) {
            triedActors[actor_name].push(flavor);
        }

        var loadedActorFlavors = this.loadedActorFlavors;
        if (!(actor_name in loadedActorFlavors)) {
            loadedActorFlavors[actor_name] = []
        }

        var created = false;
        var that = this;
        var image = null;

        var onLoaded = function(key, file) {
            if (key == flavored_actor_name) {
                if (!(that.loadedActorFlavors[actor_name].includes(flavor))) {
                    that.loadedActorFlavors[actor_name].push(flavor);
                }

                if (image != null) {
                    game.events.off('filecomplete', onLoaded);
                }

                that.addActorIfFullyLoaded(actor_name, flavor);
            }
        };

        if (this.loadedActorJavascripts.includes(actor_name)) {
            this.addActorIfFullyLoaded(actor_name, flavor);
        } else {
            var actor_url = scene_dir + '/actors/' + actor_name;
            var actor_js_url = actor_url + '/' + actor_name + '.js';
            loadJs(actor_js_url, () => {
                this.loadedActorJavascripts.push(actor_name);
                this.addActorIfFullyLoaded(actor_name, flavor);
            });
        }

        if (!(loadedActorFlavors[actor_name].includes(flavor))) {
            var path = dyn_scene_dir + '/actors/' + actor_name + '/' + flavor + '.png';
            image = game.load.image(flavored_actor_name, path);
            image.on('filecomplete', onLoaded, this);
            onceLoadingIsAllowed(() => game.load.start());
        }
    }
}
