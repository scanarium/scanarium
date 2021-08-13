// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

DeveloperMode = {
    enabled: false,
    clicksToEnable: 5,
    urlParameter: 'developerMode',

    init: function() {
        if (getUrlParameterBoolean(this.urlParameter, false)) {
            this.enter();
        }
    },

    countClick: function() {
        this.clicksToEnable--;
        var enter = (this.clicksToEnable <= 0);
        if (enter) {
            this.enter();
        }
        return enter;
    },

    enter: function() {
        if (!this.enabled) {
            FrameCounter.show();
            DeveloperInformation.show();
            this.enabled = true;
            setUrlParameterBoolean(this.urlParameter, this.enabled);
            MessageManager.addMessage(localize('Developer Mode activated'));
        } else {
            MessageManager.addMessage(localize('You are already in developer mode'));
        }
        this.clicksToEnable = 0;
    }
}
