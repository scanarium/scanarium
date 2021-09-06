# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import os

from .environment import CanaryTestCase


class RegenerateStaticContentTestCase(CanaryTestCase):
    def run_scan_data(self, args=[], expected_returncode=0):
        return self.run_cgi(None, 'regenerate-static-content', args,
                            expected_returncode=expected_returncode)

    def test_mask_svg_unfilled_version_1(self):
        scene = 'fairies'
        actor = 'RoundBug'
        self.run_scan_data([scene, actor])
        mask_file = os.path.join('scenes', scene, 'actors', actor,
                                 actor + '-mask-d-1.png')
        image = self.readImage(mask_file)
        self.assertColor(image, 352, 348, 'white', allowed_deviation=0)
        self.assertColor(image, 820, 334, 'white', allowed_deviation=0)
        self.assertColor(image, 528, 545, 'white', allowed_deviation=0)
        self.assertColor(image, 654, 229, 'white', allowed_deviation=0)
        self.assertColor(image, 0, 0, 'black', allowed_deviation=0)
        self.assertColor(image, 640, 470, 'black', allowed_deviation=0)
        self.assertColor(image, 521, 308, 'black', allowed_deviation=0)
        self.assertColor(image, 633, 273, 'black', allowed_deviation=0)

    def test_mask_svg_filled_version_1(self):
        scene = 'space'
        actor = 'Star'
        self.run_scan_data([scene, actor])
        mask_file = os.path.join('scenes', scene, 'actors', actor,
                                 actor + '-mask-d-1.png')
        image = self.readImage(mask_file)
        self.assertColor(image, 645, 355, 'white', allowed_deviation=0)
        self.assertColor(image, 641, 258, 'white', allowed_deviation=0)
        self.assertColor(image, 704, 444, 'white', allowed_deviation=0)
        self.assertColor(image, 584, 444, 'white', allowed_deviation=0)
        self.assertColor(image, 606, 313, 'black', allowed_deviation=0)
        self.assertColor(image, 644, 420, 'black', allowed_deviation=0)
        self.assertColor(image, 677, 309, 'black', allowed_deviation=0)
