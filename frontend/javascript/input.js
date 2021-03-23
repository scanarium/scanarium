document.addEventListener("keypress", function(e) {
  if (e.key === 'f') {
    canvases = document.getElementsByTagName('canvas');
    if (canvases.length) {
      canvases[0].requestFullscreen();
    }
  } else if (e.key === 'p') {
    // We (un)pause outside of the game itself, as a paused game did not handle
    // keydown events reliable and hence made it tricky to unpause.
    PauseManager.toggle();
  } else if (e.key === '?') {
    // Phaser does not offer a keycode for question mark, so we trigger from
    // outside.
    HelpPage.toggleVisibility();
  } else if (e.key in cgis) {
    var cgi = cgis[e.key];
    callCgi(cgi);
  }
}, false);


function pause_manager_toggle(event) {
  if (!event.handled_by_scanarium_settings) {
    PauseManager.toggle();
  }
}

document.addEventListener("click", pause_manager_toggle);
document.addEventListener("touchstart", pause_manager_toggle);
