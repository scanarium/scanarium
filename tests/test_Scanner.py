# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import os
import sys

SCANARIUM_DIR_ABS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCANARIUM_DIR_ABS)
from scanarium.Scanner import parse_qr
del sys.path[0]


from .environment import BasicTestCase


class ScannerTest(BasicTestCase):
    def test_parse_qr_plain(self):
        with self.prepared_environment() as dir:
            scanarium = self.new_Scanarium(dir)
            self.assertEqual(parse_qr(scanarium, 'foo:bar'), {
                    'command': 'foo',
                    'parameter': 'bar',
                    })

    def test_parse_qr_url_prefix(self):
        data = 'http://example.org/quux?qr=foo:bar'
        with self.prepared_environment() as dir:
            scanarium = self.new_Scanarium(dir)
            self.assertEqual(parse_qr(scanarium, data), {
                    'command': 'foo',
                    'parameter': 'bar',
                    })

    def test_parse_qr_unexpected_characters(self):
        data = 'http://example.org/quux?qr=fo{o:b}a]r:q+3+'
        with self.prepared_environment() as dir:
            scanarium = self.new_Scanarium(dir)
            self.assertEqual(parse_qr(scanarium, data), {
                    'command': 'fo_o',
                    'parameter': 'b_a_r',
                    'q': '3_',
                    })

    def test_parse_qr_empty_parameter(self):
        with self.prepared_environment() as dir:
            scanarium = self.new_Scanarium(dir)
            self.assertEqual(parse_qr(scanarium, 'foo:'), {
                    'command': 'foo',
                    'parameter': '',
                    })

    def test_parse_qr_empty_command(self):
        with self.prepared_environment() as dir:
            scanarium = self.new_Scanarium(dir)
            self.assertEqual(parse_qr(scanarium, ':bar'), {
                    'command': '',
                    'parameter': 'bar',
                    })

    def test_parse_qr_empty_command_and_parameter(self):
        with self.prepared_environment() as dir:
            scanarium = self.new_Scanarium(dir)
            self.assertEqual(parse_qr(scanarium, ':'), {
                    'command': '',
                    'parameter': '',
                    })

    def test_parse_qr_1_options(self):
        with self.prepared_environment() as dir:
            scanarium = self.new_Scanarium(dir)
            self.assertEqual(parse_qr(scanarium, 'foo:bar:key_value'), {
                    'command': 'foo',
                    'parameter': 'bar',
                    'key': 'value',
                    })

    def test_parse_qr_3_options(self):
        data = 'foo:bar:k1_v1:k2_v2:k3_v3'
        with self.prepared_environment() as dir:
            scanarium = self.new_Scanarium(dir)
            self.assertEqual(parse_qr(scanarium, data), {
                    'command': 'foo',
                    'parameter': 'bar',
                    'k1': 'v1',
                    'k2': 'v2',
                    'k3': 'v3',
                    })

    def test_parse_qr_empty_option(self):
        with self.prepared_environment() as dir:
            scanarium = self.new_Scanarium(dir)
            self.assertEqual(parse_qr(scanarium, 'foo:bar:_'), {
                    'command': 'foo',
                    'parameter': 'bar',
                    '': '',
                    })

    def test_parse_qr_missing_parameter(self):
        test_config = {
            'debug': {
                'fine_grained_errors': False,
                }}
        with self.prepared_environment(test_config=test_config) as dir:
            scanarium = self.new_Scanarium(dir)
            with self.assertRaisesScanariumError('SE_UNKNOWN_QR_CODE'):
                parse_qr(scanarium, 'foo')

    def test_parse_qr_missing_parameter_fine_grained(self):
        test_config = {
            'debug': {
                'fine_grained_errors': True,
                }}
        with self.prepared_environment(test_config=test_config) as dir:
            scanarium = self.new_Scanarium(dir)
            with self.assertRaisesScanariumError('SE_SCAN_MISFORMED_QR_CODE'):
                parse_qr(scanarium, 'foo')

    def test_parse_qr_scanarium_url(self):
        data = 'HTTPS://SCANARIUM.COM/032'
        test_config = {
            'qr-code': {
                'mappings': 'HTTPS://SCANARIUM.COM/@%%CONF_DIR%%/qr-code-maps/'
                'SCANARIUM.COM.json',
                }}
        with self.prepared_environment(test_config=test_config) as dir:
            scanarium = self.new_Scanarium(dir)
            self.assertEqual(parse_qr(scanarium, data), {
                    'command': 'highway',
                    'parameter': 'Bus',
                    'd': '1',
                    })
