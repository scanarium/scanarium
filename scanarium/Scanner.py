# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import json
import locale
import logging
import os
import re
import sys
import shutil

import cv2
import numpy as np

from .ScanariumError import ScanariumError
from .scanner_qr import extract_qr, parse_qr
from .scanner_camera import open_camera, close_camera, get_image
from .scanner_rectification import rectify_to_qr_parent_rect, \
    rectify_to_biggest_rect
from .scanner_util import scale_image_from_config


logger = logging.getLogger(__name__)

NEXT_RAW_IMAGE_STORE = 0  # Timestamp of when to store the next raw image.


def debug_show_image(title, image, config):
    image_hide_key = re.sub('[^0-9a-z_]+', '_', 'hide_image_' + title.lower())
    if image_hide_key[-1] == '_':
        image_hide_key = image_hide_key[:-1]
    if config.get('general', 'debug', 'boolean') and \
            not config.get('debug', 'hide_images', 'boolean'):
        if not config.get('debug', image_hide_key, 'boolean',
                          allow_missing=True):
            cv2.imshow(title, image)
            locale.resetlocale()


def create_error_unknown_qr():
    return ScanariumError(
        'SE_UNKNOWN_QR_CODE',
        'Unknown QR code')


def get_brightness_factor(scanarium):
    factor = None
    file_name = scanarium.get_config('scan', 'max_brightness',
                                     allow_empty=True)
    if file_name is not None:
        image = cv2.imread(file_name)

        brightness = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # For each pixel, brightness is a value from 0 to 255.
        # For each pixel `c` from the camera and corresponding brightness `b`
        # from the `max_brightness` image, we want to compute the effective
        # brightness `e` as
        #
        #     e = c / b * 255
        #
        # (with clipping to [0, 255] afterwards). To avoid repetitive
        # costly computations for each frame, we do not return `b` as is, but
        # we rewrite the equation as
        #
        #       e = c * f, where f = 255 / b
        #
        # (of course again with clipping to [0, 255] afterwards). In this
        # second formulation, we can compute the factor `f` ahead of time,
        # which is what this function does. This approach is better than the
        # first equation as now only a single multiplication is needed for each
        # pixel instead of a multiplication and division. This re-formulation
        # shaves off about 2/3 of computation time per frame.
        #
        # (We clip pixel with maximum brightness of 0 to 1 to avoid division by
        # zero errors. But pixels of maximum brightness 0 do not contribute
        # anyways, so this simplification does not adversely affect the result,
        # while it considerably simplifies computation.)
        factor = 255 / np.clip(brightness, 1, 255)

    return factor


def orient_image(scanarium, image):
    if image.shape[0] > image.shape[1]:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    (qr_rect, _) = extract_qr(scanarium, image)
    if qr_rect.left + qr_rect.width / 2 > image.shape[1] / 2:
        # QR Code is not on the left half of the picture. As it's landscape
        # (see above), the qr code is in the top-right corner and we need to
        # rotate 180 degrees.
        image = cv2.rotate(image, cv2.ROTATE_180)

    return image


def align_aspect_ratio(scanarium, image, target):
    target_ar = target.shape[1] / target.shape[0]
    image_ar = image.shape[1] / image.shape[0]

    # We only resize the image, if its aspect ration is too far off. So we
    # tolerate smaller mismatches to avoid resizes just because of a few
    # pixels, as each resize makes the image more mushy.
    if abs(target_ar - image_ar) > 0.05:
        if target_ar > image_ar:
            new_width = round(image.shape[0] * target_ar)
            new_height = image.shape[0]
        else:
            new_width = image.shape[1]
            new_height = round(image.shape[1] / target_ar)
        image = cv2.resize(image, (new_width, new_height), cv2.INTER_AREA)

    scanarium.debug_show_image('Aspect ratio fixed image', image)

    return image


def mask(scanarium, image, qr_parsed, visualized_alpha=None):
    scene = qr_parsed['command']
    scene_dir = os.path.join(scanarium.get_scenes_dir_abs(), scene)
    if not os.path.isdir(scene_dir):
        if scanarium.get_config('debug', 'fine_grained_errors',
                                kind='boolean'):
            raise ScanariumError('SE_UNKNOWN_SCENE',
                                 'Scene "{scene_name}" does not exist',
                                 {'scene_name': scene})
        else:
            raise create_error_unknown_qr()

    actor = qr_parsed['parameter']
    actor_dir = os.path.join(scene_dir, 'actors', actor)
    if not os.path.isdir(actor_dir):
        if scanarium.get_config('debug', 'fine_grained_errors',
                                kind='boolean'):
            raise ScanariumError(
                'SE_UNKNOWN_ACTOR',
                'Actor "{actor_name}" does not exist in scene "{scene_name}"',
                {'scene_name': scene, 'actor_name': actor})
        else:
            raise create_error_unknown_qr()

    try:
        decoration_version = int(qr_parsed.get('d', 1))
    except Exception:
        raise create_error_unknown_qr()
    mask_png_file_path = scanarium.get_versioned_filename(
        actor_dir, f'{actor}-mask-effective', 'png', decoration_version)
    if not os.path.isfile(mask_png_file_path):
        if scanarium.get_config('debug', 'fine_grained_errors',
                                kind='boolean'):
            raise ScanariumError('SE_SCAN_NO_MASK_PNG',
                                 'Failed to find mask png {file_name}',
                                 {'file_name': mask_png_file_path})
        else:
            raise create_error_unknown_qr()

    mask = cv2.imread(mask_png_file_path, 0)

    image = align_aspect_ratio(scanarium, image, mask)

    mask = cv2.resize(mask, (image.shape[1], image.shape[0]), cv2.INTER_AREA)

    channels = cv2.split(image)
    if visualized_alpha is not None:
        factor = np.clip(mask.astype(np.float32) / 255, visualized_alpha, 1)
        channels = [(channel * factor).astype(np.uint8)
                    for channel in channels]
    else:
        # We want to append the mask as alpha channel. With OpenCV 4.2.0
        # `channels` is a list. With OpenCV 4.5.5 it is a tuple, and hence
        # lacks an `append` method. So we explicitly convert to a list.
        channels = list(channels)

    channels.append(mask)
    masked = cv2.merge(channels)

    return (masked, mask_png_file_path)


def crop(scanarium, image, mask_png_file_path):
    mask_json_file_path = mask_png_file_path.split('.', 1)[0] + '.json'
    try:
        with open(mask_json_file_path, 'r') as file:
            data = json.load(file)
    except Exception:
        if scanarium.get_config('debug', 'fine_grained_errors',
                                kind='boolean'):
            raise ScanariumError('SE_SCAN_NO_MASK_JSON',
                                 'Failed to read mask json {file_name}',
                                 {'file_name': mask_json_file_path})
        else:
            raise create_error_unknown_qr()

    factor_x = image.shape[1] / data["width"]
    factor_y = image.shape[0] / data["height"]
    x_min = round(data["x_min"] * factor_x)
    x_max_inc = round(data["x_max_inc"] * factor_x)
    y_min = round(data["y_min"] * factor_y)
    y_max_inc = round(data["y_max_inc"] * factor_y)

    cropped = image[y_min:y_max_inc, x_min:x_max_inc]

    return cropped


def balance(scanarium, image):
    algo = scanarium.get_config('scan', 'white_balance').lower()
    if algo in ['simple', 'yes', 'true']:
        wb = cv2.xphoto.createSimpleWB()
        ret = wb.balanceWhite(image)
    elif algo == 'grayworld':
        wb = cv2.xphoto.createGrayworldWB()
        wb.setSaturationThreshold(0.95)
        ret = wb.balanceWhite(image)
    elif algo in ['none', 'no', 'false']:
        ret = image
    else:
        raise ScanariumError('SE_SCAN_UNKNOWN_WB',
                             'Unknown white balance filter configured')

    return ret


def embed_metadata(scanarium, file, basename, scene, actor):
    scanarium.embed_metadata(
        file, {
            'XMP-xmp': {
                'CreatorTool': 'Scanarium',
                'Label': f'scene:{scene}, actor:{actor}, v:1',
                },
            },
        )


def save_image(scanarium, image, scene, actor):
    timestamp = scanarium.get_timestamp_for_filename()
    actor_path = os.path.join(scene, 'actors', actor)
    if not os.path.isdir(os.path.join(scanarium.get_scenes_dir_abs(),
                                      actor_path)):
        # This should never happen, as masking already ensured that the actor
        # source is there. But since we're about to create directories, we're
        # extra warry.
        raise ScanariumError('SE_SCAN_SAVE_PATH_MISSING', 'Directory to '
                             'store file in does not exist, or is no '
                             'directory')

    dynamic_dir = scanarium.get_dynamic_directory()
    image_dir = os.path.join(dynamic_dir, 'scenes', actor_path)
    os.makedirs(image_dir, exist_ok=True)
    basename = f'{timestamp}.png'
    tmp_image_file = os.path.join(image_dir, 'tmp-' + basename)

    cv2.imwrite(tmp_image_file, image)
    embed_metadata(scanarium, tmp_image_file, basename, scene, actor)

    image_file = os.path.join(image_dir, basename)
    shutil.move(tmp_image_file, image_file)

    scanarium.generate_thumbnail(image_dir, basename)

    if scanarium.get_config('log', 'scanned_actor_files', kind='boolean'):
        try:
            log_filename = scanarium.get_log_filename(
                f'scanned-actor-{basename}')
            shutil.copy2(image_file, log_filename)
        except Exception as e:
            print(e, file=sys.stderr)
            # Logging failed. There's not much we can do here.
            pass

    return timestamp


def actor_image_pipeline(scanarium, image, qr_rect, qr_parsed,
                         visualized_alpha=None):
    image = rectify_to_qr_parent_rect(scanarium, image, qr_rect)
    image = orient_image(scanarium, image)
    (image, mask_file) = mask(scanarium, image, qr_parsed,
                              visualized_alpha=visualized_alpha)
    image = crop(scanarium, image, mask_file)
    image = balance(scanarium, image)

    # Finally the image is rectified, landscape, and the QR code is in the
    # lower left-hand corner, and white-balance has been run.

    (image, _) = scale_image_from_config(scanarium, image, 'final')
    scanarium.debug_show_image('Final', image)
    return image


def process_actor_image_with_qr_code(scanarium, image, qr_rect, qr_parsed):
    scene = qr_parsed['command']
    actor = qr_parsed['parameter']
    image = actor_image_pipeline(scanarium, image, qr_rect, qr_parsed)
    flavor = save_image(scanarium, image, scene, actor)

    scanarium.reindex_actors_for_scene(scene)

    return {
        'scene': scene,
        'actor': actor,
        'flavor': flavor,
    }


def process_image_with_qr_code_unlogged(scanarium, qr_parsed, image, qr_rect):
    command = qr_parsed['command']
    parameter = qr_parsed['parameter']
    if command == 'debug':
        if parameter == 'ok':
            ret = {
                'ok': True
            }
        elif parameter == 'fail':
            raise ScanariumError(
                'SE_DEBUG_FAIL',
                'Intentional error from the "debug:fail" command')
        elif parameter == 'toggleFps':
            ret = {}
        elif parameter == 'toggleDevInfo':
            ret = {}
        else:
            raise ScanariumError(
                'SE_UNKNOWN_PARAM',
                'Command "{command}" does not allow a parameter "{parameter}"',
                {'command': command, 'parameter': parameter})
    elif command == 'reset':
        ret = scanarium.reset_dynamic_content(log=False)
    elif command == 'switchScene':
        scene = parameter
        scene_dir = os.path.join(scanarium.get_scenes_dir_abs(), scene)
        if os.path.isdir(scene_dir):
            ret = {}
        else:
            raise ScanariumError('SE_UNKNOWN_SCENE',
                                 'Scene "{scene_name}" does not exist',
                                 {'scene_name': scene})
        # We opportunistically try to update the default scene in the global
        # config.json. If that updating fails, we still flag success, as the
        # clients can still switch their scene. But we log the error for the
        # admins to notice.
        try:
            dynamic_dir_abs = scanarium.get_dynamic_directory()
            json_file_abs = os.path.join(dynamic_dir_abs, 'config.json')
            config = {}
            if os.path.isfile(json_file_abs):
                with open(json_file_abs, 'r') as file:
                    config = json.load(file)
            config['default_scene'] = scene
            scanarium.dump_json(json_file_abs, config)
        except Exception:
            logger.exception(f'Failed to update {json_file_abs}')
    elif command == 'system':
        if parameter == 'poweroff':
            command = ['/usr/bin/sudo', '--non-interactive', '/sbin/poweroff']
            scanarium.run(command, timeout=10)
            ret = {
                'ok': True
            }
        else:
            raise ScanariumError(
                'SE_UNKNOWN_PARAM',
                'Command "{command}" does not allow a parameter "{parameter}"',
                {'command': command, 'parameter': parameter})
    else:
        ret = process_actor_image_with_qr_code(scanarium, image, qr_rect,
                                               qr_parsed)
    return ret


def process_image_with_qr_code(scanarium, command_logger, image, qr_rect, data,
                               should_skip_exception=None):
    qr_parsed = {
        'command': None,
        'parameter': None,
        }
    payload = {}
    exc_info = None
    try:
        qr_parsed = parse_qr(scanarium, data)

        payload = process_image_with_qr_code_unlogged(
            scanarium, qr_parsed, image, qr_rect)
    except Exception as e:
        if should_skip_exception is not None and should_skip_exception(e):
            raise ScanariumError('SE_SKIPPED_EXCEPTION',
                                 'Exception marked as skipped')
        exc_info = sys.exc_info()

    return command_logger.log(payload, exc_info, qr_parsed['command'],
                              [qr_parsed['parameter']])


class Scanner(object):
    def __init__(self, config, command_logger):
        super(Scanner, self).__init__()
        self._config = config
        self._command_logger = command_logger

    def debug_show_image(self, title, image):
        debug_show_image(title, image, self._config)

    def open_camera(self, scanarium):
        return open_camera(scanarium)

    def close_camera(self, scanarium, camera):
        return close_camera(scanarium, camera)

    def get_image(self, scanarium, camera=None):
        return get_image(scanarium, camera)

    def get_brightness_factor(self, scanarium):
        return get_brightness_factor(scanarium)

    def extract_qr(self, scanarium, image):
        return extract_qr(scanarium, image)

    def process_image_with_qr_code(self, scanarium, image, qr_rect, data,
                                   should_skip_exception=None):
        return process_image_with_qr_code(
            scanarium, self._command_logger, image, qr_rect, data,
            should_skip_exception)

    def actor_image_pipeline(self, scanarium, image, qr_rect, qr_parsed,
                             visualized_alpha=None):
        return actor_image_pipeline(
            scanarium, image, qr_rect, qr_parsed,
            visualized_alpha=visualized_alpha)

    def rectify_to_biggest_rect(self, scanarium, image,
                                yield_only_points=False):
        return rectify_to_biggest_rect(scanarium, image,
                                       yield_only_points=yield_only_points)

    def rectify_to_qr_parent_rect(self, scanarium, image, qr_rect,
                                  yield_only_points=False):
        return rectify_to_qr_parent_rect(scanarium, image, qr_rect,
                                         yield_only_points=yield_only_points)
