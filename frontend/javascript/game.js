function preload() {
    // Initing `game` to be save even if preload happens to get called before
    // `Phaser.Game` initialization can set it.
    game = this;

    this.load.image('failed', '/static/failed.png');
    this.load.image('info', '/static/info.png');
    this.load.image('none', '/static/none.png');
    this.load.image('ok', '/static/ok.png');
    this.load.image('pause', '/static/pause.png');
    this.load.image('smile', '/static/smile.png');
    this.load.image('background', scene_dir + '/background');

    scene_preload();

    ScActorManager.reloadConfigFiles();
}
scanariumConfig.scene["preload"] = preload;

function create() {
    // Initing `game` to be save even if create happens to get called before
    // `Phaser.Game` initialization can set it.
    game = this;

    var config = scanariumConfig;

    //  A simple background for our game
    background = this.add.image(0, 0, 'background');
    background.setOrigin(0, 0);
    sendToBack(background);
    LayoutManager.register(function(width, height) {
      background.setScale(width/background.width, height/background.height);
    });

    ScActorManager.init(config);

    scene_create();

    FrameCounter.init();
    PageInsertionHint.init();
    CommandLogInjector.init();
    ScreensaverManager.init();
    PauseManager.init();
    DeveloperInformation.init();
    Greeter.init();

    this.scale.on('resize', LayoutManager.onResize, this);
    LayoutManager.onResize();

    // Ideally, we would listen on Phaser.Core.Events.CONTEXT_LOST and be
    // portable. But this failed to work. So we wire it up manually.
    var canvas = game.renderer.canvas;
    if (canvas) {
        canvas.addEventListener('webglcontextlost', () => {
            // WebGL Context typically gets lost only on device under memory
            // pressure, and if the device switched to another application.
            //
            // This includes switching to the camera app to take a picture.  In
            // this case there is a race between the upload to start and the
            // WebGL context to get lost. So we sleep 100ms to make sure the
            // upload can start before we try to reload the scene.
            setTimeout(() => {
                updateLocation(true, localize('The browser lost the graphics context, which is typically fixed by automatically reloading the page.'));
            }, 100);
        });
    }
}
scanariumConfig.scene["create"] = create;

var updateLastTime = 0;
function update (time, delta) {
    // delta is way too often off. Especially, if the tab is in the
    // background. So we compute our own.
    delta = time - updateLastTime;
    FrameCounter.update(time, updateLastTime);
    PageInsertionHint.update(time);
    DeveloperInformation.update();

    scene_update(time, delta);

    ScActorManager.update(time, delta);

    if (typeof MessageManager !== 'undefined') {
      MessageManager.update(time, delta);
    }

    updateLastTime = time;
}
scanariumConfig.scene["update"] = update;
