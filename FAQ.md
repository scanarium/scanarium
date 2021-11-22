# Frequently Asked Questions

[Documentation Index](docs/index.md)

1. [Q: Did you invent it? Who came up with this concept?](#q-did-you-invent-it-who-came-up-with-this-concept)
1. [Q: Is there some public Scanarium demo instance?](#q-is-there-some-public-Scanarium-demo-instance)
1. [Q: Which webcam / camera should I use?](#q-which-webcam--camera-should-i-use)
1. [Q: How to adjust the camera and coloring page?](#q-how-to-adjust-the-camera-and-coloring-page)
1. [Q: The physics is all wrong!](#q-the-physics-is-all-wrong)
1. [Q: Going into fullscreen does not resize Scanarium to cover the whole page.](#q-going-into-fullscreen-does-not-resize-scanarium-to-cover-the-whole-page)
1. [Q: I want to backup the scanned images. Where do they get stored?](#q-i-want-to-backup-the-scanned-images-where-do-they-get-stored)



## Q: Did you invent it? Who came up with this concept?

There is [much](https://workinman.com/virtual-aquarium-design-museum)
[prior](https://dinoland.nl/en/) [art](https://www.stlouisaquarium.com/)
[in](https://9gag.com/gag/amvxwWo)
[museums](https://digitalmoo.com/products/virtual-aquarium/) around the world
when it comes to coloring and animating. It's not clear, who first allowed to
animate user-generated content and when. But there are many
[groups](https://www.youtube.com/watch?v=-tmd1hjkhIs) that offer this
functionality. And for example [teamLab](https://www.teamlab.art) has
[many](https://www.teamlab.art/w/sketch_ocean/)
[installations](https://borderless.teamlab.art/ew/aquarium/)
[in](https://www.teamlab.art/w/sketch_animals/)
[this](https://www.teamlab.art/w/sketchpeople/)
[spirit](https://www.teamlab.art/w/sketchtown/).

We've not invented it. We're not doing huge installations at museums. We're not
even doing 3D models. But we try to bring it to your living room as free
software that you can self-host without having to install any proprietary apps.



## Q: Is there some public Scanarium demo instance?

At [https://demo.scanarium.com/](https://demo.scanarium.com/) Scanarium is running
live. Uploading files has been disabled to avoid creepy content. But the site is
good enough to show what you can expect.



## Q: Which webcam / camera should I use?

See [docs/camera.md](docs/camera.md)



## Q: How to adjust the camera and coloring page?

See [docs/camera-setup.md](docs/camera-setup.md)



## Q: The physics is all wrong!

Yes, it is wrong. And it is wrong on purpose. For example angular momentum is
missing in the space scene. If we added angular momentum, spaceships would
either all start to spin at some point (as thrusters fire randomly) or we'd have
to implement counter-thrusts, to keep spaceships from spinning uncontrollably if
another thruster fired before. Neither is a good solution for a toolkit that
should be simple and easy to extend. But the physics are good enough for kids to
have fun with. And that's where we put focus.



## Q: Going into fullscreen does not resize Scanarium to cover the whole page.

Yes. This is a known issue. To get a proper fullscreen Scanarium, first go into
fullscreen mode by pressing `F11`. Then reload the page by pressing `F5`. This
should give you a fullscreen Scanarium that covers the whole display.

During development Phaser 3.11 crashed Scanarium a few times when implementing
resizing after going into full-screen. With current Phaser 3.24 the crashing
would be resolved and fullscreen reliably resizes the game. Phaser 3.24 however
seems to render the rocket thrusts for the space scene flaky. So we do not
upgrade the used Phaser until we got to the bottom of the thrust issue.



## Q: I want to backup the scanned images. Where do they get stored?

In the default setup, they'll end up at
`dynamic/scenes/$SCENE/actors/$ACTOR/*.png`.



[Documentation Index](docs/index.md)
