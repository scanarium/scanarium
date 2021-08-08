// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class ActorManagerActorReaper {
    constructor(actorManager) {
        this.actorManager = actorManager;
        this.destroyCallbacks = [];
    }

    deleteOutlyingActors() {
        var that = this;
        this.actorManager.actors.forEach(function (actor, index) {
            if ((actor.x < -actor.destroyOffset)
                || (actor.x > actor.destroyOffset + scanariumConfig.width)
                || (actor.y < -actor.destroyOffset)
                || (actor.y > actor.destroyOffset + scanariumConfig.height)) {
                that.deleteActor(actor);
            }
        });
    }

    deleteActor(actor) {
        var idx = this.actorManager.actors.indexOf(actor);
        this.actorManager.actors.splice(idx, 1);
        this.destroyCallbacks.forEach(function (callbackConfig) {
            if (callbackConfig.actor == null || callbackConfig.actor == actor.actorName) {
                callbackConfig.callback(actor);
            }
        });
        actor.destroy();
    }

    onActorDestroy(callback, actor) {
        if (typeof actor === 'undefined') {
            actor == null;
        }
        this.destroyCallbacks.push({
            callback: callback,
            actor: actor
        });
    }
}
