# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import json
import os
import re

import cv2
from pyzbar import pyzbar

from .ScanariumError import ScanariumError


def raise_error_misformed_qr_code(scanarium):
    if scanarium.get_config('debug', 'fine_grained_errors', kind='boolean'):
        raise ScanariumError('SE_SCAN_MISFORMED_QR_CODE',
                             'QR code contains misformed data')
    else:
        raise ScanariumError('SE_UNKNOWN_QR_CODE', 'Unknown QR code')


def extract_qr(scanarium, image):
    # With low light images, the random noise in different color channels is
    # typically in the way of robust detection. So we convert to
    # grey to smoothen out the noise a bit.
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    codes = pyzbar.decode(image)
    codes_len = len(codes)
    if codes_len < 1:
        raise ScanariumError('SE_SCAN_NO_QR_CODE',
                             'Failed to find QR code in image')

    if codes_len > 1:
        raise ScanariumError(
            'SE_SCAN_TOO_MANY_QR_CODES',
            'Expected to find one QR code in image, but found '
            '{qr_codes_count}',
            {'qr_codes_count': codes_len})

    code = codes[0]

    rect = code.rect

    try:
        data_bytes = code.data
        assert len(data_bytes) <= 64  # Prohibit suspicously long tags
        data = data_bytes.decode('ascii')
    except Exception:
        raise_error_misformed_qr_code(scanarium)

    return (rect, data)


def expand_qr(scanarium, data):
    mapping_specs = scanarium.get_config('qr-code', 'mappings',
                                         allow_empty=True)
    if mapping_specs:
        mapped = False
        for mapping_spec in mapping_specs.split(','):
            if not mapped:
                mapping_parts = mapping_spec.split('@')
                prefix = mapping_parts[0].strip()
                if data.startswith(prefix):
                    mapped = True
                    data = data[len(prefix):]
                    if len(mapping_parts) > 1:
                        file = mapping_parts[1].strip()
                        if file.startswith('%CONF_DIR%'):
                            file = os.path.join(scanarium.get_config_dir_abs(),
                                                file[11:])
                        with open(file, 'rt') as f:
                            code_map = json.load(f)

                        data = code_map.get(data, data)
    return data


def parse_qr(scanarium, data):
    parsed = {}
    try:
        data = expand_qr(scanarium, data)
        data = data.rsplit('/', 1)[-1].rsplit('?', 1)[-1].rsplit('=', 1)[-1]
        data = re.sub('[^0-9a-zA-Z:_]+', '_', data)
        parts = data.split(':')
        if len(parts) < 2:
            raise ValueError('Too few : separated parts')
        parsed['command'] = parts[0]
        parsed['parameter'] = parts[1]
        for kv in parts[2:]:
            (k, v) = kv.split('_', 1)
            parsed[k] = v
    except ValueError:
        raise_error_misformed_qr_code(scanarium)

    return parsed