# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import unittest
import collections.abc
import configparser
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import traceback

import cv2

SCANARIUM_DIR_ABS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCANARIUM_DIR_ABS)
from scanarium import Scanarium, ScanariumError
del sys.path[0]

FIXTURE_DIR = os.path.join('tests', 'fixtures')
COLORS = {
    'red': [0, 0, 255],
    'green': [0, 255, 0],
    'blue': [255, 0, 0],
    'white': [255, 255, 255],
    'black': [0, 0, 0],
}


class NotCleanedUpTemporaryDirectory(object):
    def __init__(self, prefix):
        self.name = tempfile.mkdtemp(prefix=prefix)

    def __enter__(self):
        return self.name

    def __exit__(self, exc, value, tb):
        pass


class AssertRaisesScanariumErrorContext(object):
    def __init__(self, test_case, expected_code):
        self.test_case = test_case
        self.exception = None
        self.expected_code = expected_code

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.test_case.fail(
                'No exception got thrown, but expected ScanariumError with '
                f'code "{self.expected_code}"')
        if issubclass(exc_type, ScanariumError):
            self.test_case.assertEqual(
                exc_val.code, self.expected_code,
                f'Raised ScanariumError has code "{exc_val.code}", but "'
                f'expected "{self.expected_code}"')
        else:
            return False
        traceback.clear_frames(exc_tb)
        return True


class BasicTestCase(unittest.TestCase):
    def get_fixture_file_name(self, name):
        return os.path.join(FIXTURE_DIR, name)

    def add_fixture(self, name, dir):
        src = self.get_fixture_file_name(name)
        dest = os.path.join(dir, name)
        if os.path.isdir(src):
            shutil.copytree(src, dest)
        else:
            shutil.copy(src, dest)

    def update_dict(self, target, source, merge_lists=False):
        for key, value in source.items():
            if isinstance(value, collections.abc.Mapping):
                repl = self.update_dict(target.get(key, {}), value)
                target[key] = repl
            elif merge_lists and isinstance(value, list) \
                    and isinstance(target.get(key, 0), list):
                target[key] += value
            else:
                target[key] = source[key]
        return target

    def prepared_environment(self, name=None, cleanup=True, test_config={}):
        temp_dir_cls = tempfile.TemporaryDirectory if cleanup \
            else NotCleanedUpTemporaryDirectory
        ctx = temp_dir_cls(prefix='scanarium-test-')
        dir = ctx.name

        dynamic_dir = os.path.join(dir, 'dynamic')
        log_dir = os.path.join(dir, 'log')

        if name:
            self.add_fixture(name, ctx.name)

        overrides = {
            'general': {
                'debug': 'False',
                },
            'directories': {
                'dynamic': dynamic_dir,
                'log': log_dir,
                },
            'log': {
                'cgi_results': False,
                'cgi_date': False,
                'scanned_actor_files': False,
                'raw_image_files': False,
                },
            'scan': {
                'source': '/dev/null',
                'max_raw_width': 1000,
                'max_raw_height': 1000,
                'max_final_width': 1000,
                'max_final_height': 1000,
            },
        }
        overrides = self.update_dict(overrides, test_config)

        for section, options in overrides.items():
            for option, value in options.items():
                if isinstance(value, str):
                    options[option] = value\
                        .replace('%DYNAMIC_DIR%', dynamic_dir)\
                        .replace('%TEST_DIR%', dir)
        config = configparser.ConfigParser()
        for section, options in overrides.items():
            config[section] = options

        with open(os.path.join(dir, 'override.conf'), 'w') as configfile:
            config.write(configfile)

        return ctx

    def new_Scanarium(self, dir):
        sys.argv = [
            '',
            '--debug-config-override',
            os.path.join(dir, 'override.conf'),
            ]
        return Scanarium()

    def flatten(self, x):
        ret = []
        if isinstance(x, list):
            for element in x:
                ret += self.flatten(element)
        else:
            ret = [x]
        return ret

    def setFile(self, file_name, contents='', mtime=None):
        flat_file_name = os.path.join(*self.flatten(file_name))
        os.makedirs(os.path.dirname(flat_file_name), exist_ok=True)
        with open(flat_file_name, 'w') as file:
            file.write(contents)
        if mtime is not None:
            os.utime(flat_file_name, (mtime, mtime))

    def get_file_contents(self, file_name, text=True):
        flat_file_name = os.path.join(*self.flatten(file_name))
        with open(flat_file_name, 'r' + ('t' if text else 'b')) as file:
            contents = file.read()
        return contents

    def get_json_file_contents(self, file_name):
        return json.loads(self.get_file_contents(file_name))

    def assertRegularFileExists(self, file_name):
        self.assertTrue(
            os.path.isfile(file_name) and not os.path.islink(file_name),
            'File "{file_name}" does not exist or not a file'
            )

    def assertPathMissing(self, file_name):
        self.assertFalse(
            os.path.exists(file_name),
            'Path "{file_name}" exists'
            )

    def assertFileJsonContents(self, file_name, expected):
        actual = self.get_json_file_contents(file_name)
        self.assertEqual(actual, expected)

    def assertFileContents(self, file_name, expected):
        actual = self.get_file_contents(file_name)
        self.assertEqual(actual, expected)

    def assertFileContains(self, file_name, expected):
        self.assertIn(expected, self.get_file_contents(file_name))

    def assertSameFileContents(self, fileA, fileB):
        contentsA = self.get_file_contents(fileA, text=False)
        contentsB = self.get_file_contents(fileB, text=False)
        # no 'assertEqual' as we're typically using this method for
        # binary data
        self.assertTrue(contentsA == contentsB)

    def assertLenIs(self, lst, expected_length):
        self.assertEqual(len(lst), expected_length,
                         f'Length of {lst} is not {expected_length}')

    def assertFullMatch(self, pattern, string):
        self.assertTrue(
            re.fullmatch(pattern, string),
            f'"{string}" does not match "{pattern}" fully'
            )

    def assertRaisesScanariumError(self, code):
        return AssertRaisesScanariumErrorContext(self, code)

    def assertRoughlyEqual(self, actual, expected, scale=None,
                           allowed_deviation=0.02):
        if scale is None:
            scale = expected
        self.assertGreaterEqual(actual, expected - scale * allowed_deviation)
        self.assertLessEqual(actual, expected + scale * allowed_deviation)

    def resolveColor(self, color):
        color = COLORS.get(color, color)
        if len(color) < 4:
            color.append(255)
        return color

    def assertColor(self, image, x, y, expected, allowed_deviation=5):
        pixel = image[y][x]
        expected = self.resolveColor(expected)

        pixel_len = len(pixel)
        if pixel_len < 4 and expected[3] != 255:
            self.fail('Expecting non-opaque alpha, but pixel has only '
                      f'{pixel_len} channels')

        for i in range(pixel_len):
            try:
                self.assertRoughlyEqual(pixel[i], expected[i], scale=255,
                                        allowed_deviation=allowed_deviation)
            except self.failureException as e:
                self.fail(f'Pixel at x: {x}, y: {y} is {pixel} and does not '
                          f'match {expected} ({e.args})')

    def readImage(self, file):
        return cv2.imread(file, cv2.IMREAD_UNCHANGED)


class CanaryTestCase(BasicTestCase):
    def run_command(self, command, expected_returncode=0):
        process = subprocess.run(command,
                                 check=False,
                                 timeout=3,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)

        if process.returncode != expected_returncode:
            raise subprocess.CalledProcessError(
                process.returncode, process.args, process.stdout,
                process.stderr)

        return {
            'stdout': process.stdout,
            'stderr': process.stderr,
        }

    def run_cgi(self, dir, cgi, arguments=[], expected_returncode=0):
        cgi_file = os.path.join('.', 'backend', f'{cgi}.py')

        standard_arguments = []

        if dir is not None:
            standard_arguments += [
                '--debug-config-override', os.path.join(dir, 'override.conf')]

        command = [cgi_file] + standard_arguments + arguments

        return self.run_command(command,
                                expected_returncode=expected_returncode)
