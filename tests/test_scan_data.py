# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import unittest
import base64
import os

from .environment import CanaryTestCase


class ScanDataCanaryTestCase(CanaryTestCase):
    def run_scan_data(self, dir, file, expected_returncode):
        with open(os.path.join(dir, file), 'rb') as f:
            raw_data = f.read()

        encoded = base64.standard_b64encode(raw_data).decode()

        return self.run_cgi(dir, 'scan-data', [encoded],
                            expected_returncode=expected_returncode)

    def run_scan_data_ok(self, dir, file):
        return self.run_scan_data(dir, file, expected_returncode=0)

    def run_scan_data_failure(self, error_code, dir, file):
        ret = self.run_scan_data(dir, file, expected_returncode=1)
        self.assertErrorCode(error_code, ret, dir)
        return ret

    def assertMarker(self, image, marker, x_factor, y_factor):
        unscaled_center_x, unscaled_center_y, unscaled_width, color = marker
        center_x = round(unscaled_center_x * x_factor)
        center_y = round(unscaled_center_y * y_factor)
        self.assertColorApproximately(image, center_x, center_y, color)

    def assertScanOk(self, dir, scene='space', actor='SimpleRocket',
                     dimension=[0, 0], markers=[]):
        scan_target_dir = os.path.join(dir, 'dynamic', 'scenes', scene,
                                       'actors', actor)
        scan_result_file = None
        for file in os.listdir(scan_target_dir):
            if file.endswith('.png'):
                # A png in the scan target directory. That has to be the
                # result of the scan.
                scan_result_file = os.path.join(scan_target_dir, file)

        self.assertIsNotNone(scan_result_file)
        image = self.readImage(scan_result_file)

        # Scanned image has been loaded. Now on to testing the scan result
        # (image.shape is (height, width, ...), dimension is (width, height).
        self.assertRoughlyEqual(image.shape[1], dimension[0])
        self.assertRoughlyEqual(image.shape[0], dimension[1])

        x_factor = image.shape[1] / dimension[0]
        y_factor = image.shape[0] / dimension[1]
        for marker in markers:
            self.assertMarker(image, marker, x_factor, y_factor)

    def assertErrorCode(self, code, command_output, dir):
        self.assertIn(code, command_output['stdout'])
        command_log_file = os.path.join(dir, 'dynamic', 'command-log.json')
        self.assertFileContains(command_log_file, code)

    def template_test_file_type(self, file_type='png', pipeline=None,
                                variant='optimal', fixture=None,
                                extra_fixture=None, config={}):
        if fixture is None:
            fixture = f'space-SimpleRocket-{variant}.{file_type}'
        test_config = self.update_dict({}, config)
        test_config = self.update_dict(test_config, {
                'scan': {f'permit_file_type_{file_type}': True}})
        if pipeline is not None:
            test_config['scan'][f'pipeline_file_type_{file_type}'] = pipeline
        with self.prepared_environment(fixture,
                                       test_config=test_config) as dir:
            if extra_fixture:
                self.add_fixture(extra_fixture, dir)

            self.run_scan_data_ok(dir, fixture)

            if file_type == 'pdf':
                self.assertScanOk(dir,
                                  dimension=[539, 371],
                                  markers=[
                                      [4, 185, 5, 'red'],
                                      [536, 5, 5, 'green'],
                                      [536, 365, 5, 'blue'],
                                  ])
            elif variant == '35':
                self.assertScanOk(dir,
                                  dimension=[304, 209],
                                  markers=[
                                      [2, 104, 5, 'red'],
                                      [300, 3, 5, 'green'],
                                      [300, 206, 5, 'blue'],
                                  ])
            else:
                self.assertScanOk(dir,
                                  dimension=[455, 313],
                                  markers=[
                                      [3, 155, 5, 'red'],
                                      [451, 3, 5, 'green'],
                                      [451, 308, 5, 'blue'],
                                  ])

            command_log_file = os.path.join(dir, 'dynamic', 'command-log.json')
            logged_result = self.get_json_file_contents(command_log_file)[0]
            self.assertTrue(logged_result['is_ok'])
            self.assertEqual(logged_result['command'], 'space')
            self.assertEqual(logged_result['parameters'], ['SimpleRocket'])

    def test_ok_png_native(self):
        self.template_test_file_type('png', pipeline='native')

    def test_ok_png_35_native(self):
        self.template_test_file_type('png', pipeline='native', variant='35')

    def test_ok_png_90_native(self):
        self.template_test_file_type('png', pipeline='native', variant='90')

    def test_ok_png_180_native(self):
        self.template_test_file_type('png', pipeline='native', variant='180')

    def test_ok_png_270_native(self):
        self.template_test_file_type('png', pipeline='native', variant='270')

    def test_ok_png_convert(self):
        self.template_test_file_type('png', pipeline='convert')

    def test_ok_jpg_native(self):
        self.template_test_file_type('jpg', pipeline='native')

    def test_ok_jpg_convert(self):
        self.template_test_file_type('jpg', pipeline='convert')

    @unittest.skipIf('TEST_SKIP_HEIC' in os.environ
                     and os.environ['TEST_SKIP_HEIC'].lower() == 'yes',
                     'Environment variable TEST_SKIP_HEIC is True')
    def test_ok_heic(self):
        self.template_test_file_type('heic')

    def test_ok_pdf_convert(self):
        self.template_test_file_type('pdf', pipeline='convert')

    def test_ok_pdf_pdftoppm(self):
        self.template_test_file_type('pdf', pipeline='pdftoppm')

    def test_ok_map_simple_prefix(self):
        config = {'qr-code': {'mappings': 'foo'}}
        self.template_test_file_type(
            fixture='qr-foospace-SimpleRocket.png',
            config=config,
            pipeline='native')

    def test_ok_map_proper_map_unmatched(self):
        config = {'qr-code': {
                'mappings': 'foo@%TEST_DIR%/qr-code-map-bar.json'}}
        self.template_test_file_type(
            fixture='qr-foospace-SimpleRocket.png',
            config=config,
            pipeline='native',
            extra_fixture='qr-code-map-bar.json')

    def test_ok_map_proper_map_matched(self):
        config = {'qr-code': {
                'mappings': 'foo@%TEST_DIR%/qr-code-map-bar.json'}}
        self.template_test_file_type(
            fixture='qr-fooquux.png',
            config=config,
            pipeline='native',
            extra_fixture='qr-code-map-bar.json')

    def test_fail_png_contrast_selection_only_high_contrast(self):
        with self.assertRaises(AssertionError):
            config = {'scan': {'contrasts': '10'}}
            self.template_test_file_type('png', pipeline='native',
                                         variant='contrast-check',
                                         config=config)

    def test_ok_png_contrast_selection(self):
        config = {'scan': {'contrasts': '10, 1'}}
        self.template_test_file_type('png', pipeline='native',
                                     variant='contrast-check', config=config)

    def test_ok_decoration_version_1(self):
        self.template_test_file_type('png', pipeline='native', variant='d-1')

    def test_fail_pipeline_os_error_fine(self):
        fixture = 'space-SimpleRocket-optimal.png'
        config = {
            'programs': {
                'convert_untrusted': os.path.join('%DYNAMIC_DIR%', 'foo'),
                },
            'scan': {
                'permit_file_type_png': True,
                'pipeline_file_type_png': 'convert',
                },
            'debug': {
                'fine_grained_errors': True,
                },
            }
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_PIPELINE_OS_ERROR', dir, fixture)

    def test_fail_pipeline_os_error(self):
        fixture = 'space-SimpleRocket-optimal.png'
        config = {
            'programs': {
                'convert_untrusted': os.path.join('%DYNAMIC_DIR%', 'foo'),
                },
            'scan': {
                'permit_file_type_png': True,
                'pipeline_file_type_png': 'convert',
                },
            }
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_PIPELINE_ERROR', dir, fixture)

    def test_fail_pipeline_return_value_fine(self):
        fixture = 'space-SimpleRocket-optimal.png'
        config = {
            'programs': {
                'convert_untrusted': '/bin/false',
                },
            'scan': {
                'permit_file_type_png': True,
                'pipeline_file_type_png': 'convert',
                },
            'debug': {
                'fine_grained_errors': True,
                },
            }
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure(
                'SE_PIPELINE_RETURN_VALUE', dir, fixture)

    def test_fail_pipeline_return_value(self):
        fixture = 'space-SimpleRocket-optimal.png'
        config = {
            'programs': {
                'convert_untrusted': '/bin/false',
                },
            'scan': {
                'permit_file_type_png': True,
                'pipeline_file_type_png': 'convert',
                },
            }
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_PIPELINE_ERROR', dir, fixture)

    def test_fail_no_rectangle(self):
        fixture = 'blank-white.png'
        config = {'scan': {'permit_file_type_png': True}}
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_SCAN_NO_QR_CODE', dir, fixture)

    def test_fail_only_rectangle(self):
        fixture = 'only-rect.png'
        config = {'scan': {'permit_file_type_png': True}}
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_SCAN_NO_QR_CODE', dir, fixture)

    def test_fail_only_qr(self):
        fixture = 'only-qr.png'
        config = {'scan': {'permit_file_type_png': True}}
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_SCAN_NO_APPROX', dir, fixture)

    def test_fail_too_small(self):
        fixture = 'too-small.png'
        config = {'scan': {'permit_file_type_png': True}}
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_SCAN_IMAGE_TOO_SMALL', dir, fixture)

    def test_fail_grew_too_small_fine(self):
        fixture = 'grew-too-small.png'
        config = {
            'scan': {'permit_file_type_png': True},
            'debug': {'fine_grained_errors': True},
            }
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure(
                'SE_SCAN_IMAGE_GREW_TOO_SMALL', dir, fixture)

    def test_fail_grew_too_small_general(self):
        fixture = 'grew-too-small.png'
        config = {'scan': {'permit_file_type_png': True}}
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_SCAN_NO_QR_CODE', dir, fixture)

    def test_fail_too_many_iterations_fine(self):
        fixture = 'too-many-iterations.png'
        config = {
            'scan': {'permit_file_type_png': True},
            'debug': {'fine_grained_errors': True},
            }
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure(
                'SE_SCAN_IMAGE_TOO_MANY_ITERATIONS', dir, fixture)

    def test_fail_too_many_iterations_general(self):
        fixture = 'too-many-iterations.png'
        config = {'scan': {'permit_file_type_png': True}}
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_SCAN_NO_QR_CODE', dir, fixture)

    def test_fail_too_many_qr_codes(self):
        fixture = 'too-many-qrs.png'
        config = {'scan': {'permit_file_type_png': True}}
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure(
                'SE_SCAN_TOO_MANY_QR_CODES', dir, fixture)

    def test_fail_qr_foo_fine(self):
        fixture = 'qr-foo.png'
        config = {
            'scan': {'permit_file_type_png': True},
            'debug': {'fine_grained_errors': True},
            }
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure(
                'SE_SCAN_MISFORMED_QR_CODE', dir, fixture)

    def test_fail_qr_foo(self):
        fixture = 'qr-foo.png'
        config = {'scan': {'permit_file_type_png': True}}
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_UNKNOWN_QR_CODE', dir, fixture)

    def test_fail_qr_foo_bar_baz_fine(self):
        fixture = 'qr-foo-bar.png'
        config = {
            'scan': {'permit_file_type_png': True},
            'debug': {'fine_grained_errors': True},
            }
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_UNKNOWN_SCENE', dir, fixture)

    def test_fail_qr_foo_bar_baz(self):
        fixture = 'qr-foo-bar.png'
        config = {'scan': {'permit_file_type_png': True}}
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_UNKNOWN_QR_CODE', dir, fixture)

    def test_fail_qr_space_foo_fine(self):
        fixture = 'qr-space-foo.png'
        config = {
            'scan': {'permit_file_type_png': True},
            'debug': {'fine_grained_errors': True},
            }
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_UNKNOWN_ACTOR', dir, fixture)

    def test_fail_qr_space_foo(self):
        fixture = 'qr-space-foo.png'
        config = {'scan': {'permit_file_type_png': True}}
        with self.prepared_environment(fixture, test_config=config) as dir:
            self.run_scan_data_failure('SE_UNKNOWN_QR_CODE', dir, fixture)
