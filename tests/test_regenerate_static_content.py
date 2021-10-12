# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import os

from .environment import CanaryTestCase


class RegenerateStaticContentTestCase(CanaryTestCase):
    def run_regenerate_static_content(self, args=[], expected_returncode=0):
        return self.run_cgi(None, 'regenerate-static-content', args,
                            expected_returncode=expected_returncode)

    def test_mask_svg_unfilled_version_1(self):
        scene = 'fairies'
        actor = 'RoundBug'
        self.run_regenerate_static_content([scene, actor])
        mask_file = os.path.join('scenes', scene, 'actors', actor,
                                 actor + '-mask-effective-d-1.png')
        image = self.readImage(mask_file)
        self.assertColor(image, 352, 348, 'white')
        self.assertColor(image, 820, 334, 'white')
        self.assertColor(image, 528, 545, 'white')
        self.assertColor(image, 654, 229, 'white')
        self.assertColor(image, 0, 0, 'black')
        self.assertColor(image, 640, 470, 'black')
        self.assertColor(image, 521, 308, 'black')
        self.assertColor(image, 633, 273, 'black')

    def test_mask_svg_filled_version_1(self):
        scene = 'space'
        actor = 'Star'
        self.run_regenerate_static_content([scene, actor])
        mask_file = os.path.join('scenes', scene, 'actors', actor,
                                 actor + '-mask-effective-d-1.png')
        image = self.readImage(mask_file)
        self.assertColor(image, 645, 355, 'white')
        self.assertColor(image, 641, 258, 'white')
        self.assertColor(image, 704, 444, 'white')
        self.assertColor(image, 584, 444, 'white')
        self.assertColor(image, 606, 313, 'black')
        self.assertColor(image, 644, 420, 'black')
        self.assertColor(image, 677, 309, 'black')

    def test_mask_svg_version_1(self):
        scene = 'balloons'
        actor = 'BunnyBalloon'
        self.run_regenerate_static_content([scene, actor])
        mask_file = os.path.join('scenes', scene, 'actors', actor,
                                 actor + '-mask-effective-d-1.png')
        image = self.readImage(mask_file)
        self.assertColor(image, 660, 283, 'black')
        self.assertColor(image, 696, 270, 'white')
        self.assertColor(image, 729, 261, 'black')
        self.assertColor(image, 765, 273, 'white')
        self.assertColor(image, 796, 282, 'black')
        self.assertColor(image, 726, 548, 'white')

    def test_mask_svg_version_2(self):
        scene = 'balloons'
        actor = 'BunnyBalloon'
        self.run_regenerate_static_content([scene, actor])
        mask_file = os.path.join('scenes', scene, 'actors', actor,
                                 actor + '-mask-effective-d-2.png')
        image = self.readImage(mask_file)
        self.assertColor(image, 428, 261, 'black')
        self.assertColor(image, 462, 233, 'white')
        self.assertColor(image, 501, 234, 'black')
        self.assertColor(image, 538, 248, 'white')
        self.assertColor(image, 572, 261, 'black')
        self.assertColor(image, 496, 524, 'white')

    def test_mask_json_version_1(self):
        scene = 'fairies'
        actor = 'RoundBug'
        self.run_regenerate_static_content([scene, actor])
        mask_file = os.path.join('scenes', scene, 'actors', actor,
                                 actor + '-mask-effective-d-1.json')

        expected = {
            "height": 703,
            "width": 994,
            "x_max_inc": 827,
            "x_min": 341,
            "y_max_inc": 556,
            "y_min": 221,
            }

        self.assertFileJsonContents(mask_file, expected)

    def test_generated_jpg(self):
        scene = 'space'
        actor = 'SimpleRocket'
        name = 'Einfache-Rakete.jpg'

        actor_dir = os.path.join('scenes', scene, 'actors', actor)
        file = os.path.join(actor_dir, 'pdfs', 'de', name)
        image = self.readImage(file)

        self.assertColor(image, 13, 15, 'white')
        self.assertColor(image, 95, 124, 'black')
        self.assertColor(image, 540, 336, 'white')
        self.assertColor(image, 1036, 616, 'white')

    def test_generated_png(self):
        scene = 'space'
        actor = 'SimpleRocket'
        name = 'Einfache-Rakete.png'

        actor_dir = os.path.join('scenes', scene, 'actors', actor)
        file = os.path.join(actor_dir, 'pdfs', 'de', name)
        image = self.readImage(file)

        self.assertColor(image, 13, 15, 'white')
        self.assertColor(image, 95, 124, 'black')
        self.assertColor(image, 540, 336, 'white')
        self.assertColor(image, 1036, 616, 'white')

    def test_generated_pdf(self):
        scene = 'space'
        actor = 'SimpleRocket'
        name = 'Einfache-Rakete.pdf'

        actor_dir = os.path.join('scenes', scene, 'actors', actor)
        file = os.path.join(actor_dir, 'pdfs', 'de', name)

        scanarium = self.new_Scanarium()
        actual_format = scanarium.guess_image_format(file)
        self.assertEqual(actual_format, 'pdf')

    def test_generated_thumbnail(self):
        scene = 'space'
        actor = 'SimpleRocket'
        name = 'Einfache-Rakete-thumb.jpg'

        actor_dir = os.path.join('scenes', scene, 'actors', actor)
        file = os.path.join(actor_dir, 'pdfs', 'de', name)
        image = self.readImage(file)

        self.assertColor(image, 3, 33, 'white')
        self.assertColorApproximately(image, 7, 33, 'black')
        self.assertColor(image, 16, 33, 'white')
        self.assertColor(image, 82, 50, 'white')
