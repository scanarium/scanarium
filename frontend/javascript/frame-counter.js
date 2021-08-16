// This file is part of Scanarium https://scanarium.com/ and licensed under the
// GNU Affero General Public License v3.0 (See LICENSE.md)
// SPDX-License-Identifier: AGPL-3.0-only

var FrameCounter = {
    frameCountInterval: 1000, //milli-seconds
    frameCount: 0,
    sprite: null,
    labelPrefix: 'fps: {fps}',
    urlParameter: 'showFrameCounter',

    init: function() {
        this.setVisibility(getUrlParameterBoolean(this.urlParameter, false));
    },

    isVisible: function() {
        return FrameCounter.sprite != null;
    },

    setVisibility: function(visibility) {
        visibility = !!visibility;
        if (FrameCounter.isVisible() != !!visibility) {
            if (visibility) {
                FrameCounter.sprite = game.add.text(0, 0, '', getFontStyle());
                FrameCounter.relayout();
                FrameCounter.formatCount('?');
                bringToFront(FrameCounter.sprite);
            } else {
                FrameCounter.sprite.destroy();
                FrameCounter.sprite = null;
            }
            setUrlParameterBoolean(FrameCounter.urlParameter, visibility);
        }
    },

    toggleVisibility: function() {
        FrameCounter.setVisibility(!FrameCounter.isVisible());
    },

    show: function() {
        FrameCounter.setVisibility(true);
    },

    hide: function() {
        FrameCounter.setVisibility(false);
    },

    formatCount: function(count) {
        if (this.sprite != null) {
            this.sprite.setText(localize(this.labelPrefix, {'fps': count}));
        }
    },

    update: function(time, lastTime) {
        if (this.sprite) {
            if (Math.floor(lastTime / this.frameCountInterval) == Math.floor(time / this.frameCountInterval)) {
                this.frameCount++;
            } else {
                this.formatCount(this.frameCount);
                this.frameCount=1;
            }
        }
    },

    relayout: function() {
        if (FrameCounter.sprite) {
            FrameCounter.sprite.x = 32 * window.devicePixelRatio;
            FrameCounter.sprite.y = scanariumConfig.height - 32 * window.devicePixelRatio;
        }
    },
};
LayoutManager.register(FrameCounter.relayout);
