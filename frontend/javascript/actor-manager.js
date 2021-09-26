// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class ActorManager {
    constructor() {
        this.nextConfigFetch = 0;

        this.actors = [];
        this.nextSpawn = 999999999999999; // This gets reset once configs are loaded.
        this.statsTracker = new ActorManagerStatsTracker(this);
        this.reaper = new ActorManagerActorReaper(this);
        var that = this;
        this.configLoader = new ActorManagerConfigLoader(this, () => that.nextSpawn = 0);
        this.actorCreator = new ActorManagerActorCreator(this, this.configLoader, this.statsTracker);
        this.queues = {}
    }

    preload() {
        this.configLoader.reload();
    }

    update(time, delta) {
        if (time > this.nextConfigFetch) {
            this.nextConfigFetch = time + getConfig('actor-reload-period');
            this.configLoader.reload();
        }

        if (time > this.nextSpawn) {
            // Add new actors only, if the tab is visible.
            // Otherwise, background tabs amass actors.
            if (document.visibilityState === 'visible') {
                this.loadCreateAndAddActor();
            }
            this.nextSpawn = time + getConfig('spawnPeriod');
        }

        var that = this;
        this.actors.forEach(function (actor, index) {
            actor.update(time, delta);
        });

        this.reaper.deleteOutlyingActors();
    }

    getActorCount(actorName) {
      var ret = 0;
      this.actors.forEach(function (actor, index) {
        if (actorName == actor.actorName) {
          ret += 1;
        }
      });
      return ret;
    }

    loadCreateAndAddActor(actor_name, flavor, parameters) {
        this.actorCreator.loadCreateAndAddActor(actor_name, flavor, parameters);
    }

    deleteActor(actor) {
        this.reaper.deleteActor(actor);
    }

    onActorDestroy(callback, actor) {
        this.reaper.onActorDestroy(callback, actor);
    }

    registerActor(clazz) {
        this.actorCreator.registerActor(clazz);
    }

    addToQueue(queue, actor) {
        var entries = this.getQueue(queue);
        if (entries.length > 10) {
            entries.shift();
        }
        entries.push({name: actor.actorName, flavor: actor.actorFlavor});
        this.queues[queue] = entries;
    }

    getQueue(queue) {
        var entries = [];
        if (queue in this.queues) {
            entries = this.queues[queue];
        }
        return entries;
    }

    createFromQueue(queue, parameters) {
        var entries = this.getQueue(queue);
        var ret = null;
        if (entries.length > 0) {
            var entry = entries[chooseInt(0, entries.length - 1)];
            ret = this.actorCreator.createFullyLoadedActor(entry.name, entry.flavor, parameters);
        }
        return ret;
    }
};
var actorManager = new ActorManager();
