// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

class ActorManagerStatsTracker {
    constructor(actorManager) {
        this.actorManager = actorManager;
        this.created = 0;
        DeveloperInformation.register(() => this.actorInfo(this));
    }

    trackCreation() {
        this.created += 1
    }

    actorInfo(tracker) {
      return 'actorManager: created: ' + tracker.created + ', active: ' + tracker.actorManager.actors.length;
    }
}
