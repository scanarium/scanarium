# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import os
import tempfile
import time
import shutil

import cv2

from .ScanariumError import ScanariumError
from .scanner_util import scale_image_from_config


def create_error_pipeline():
    return ScanariumError(
        'SE_PIPELINE_ERROR',
        'Server-side image processing failed')


def get_camera_type(scanarium):
    ret = 'PROPER-CAMERA'

    file_path = scanarium.get_config('scan', 'source')
    if file_path.startswith('image:'):
        ret = 'STATIC-IMAGE-CAMERA'

    return ret


def open_camera(scanarium):
    camera = None
    camera_type = get_camera_type(scanarium)
    if camera_type == 'PROPER-CAMERA':
        source = scanarium.get_config('scan', 'source')
        if source.startswith('cam:'):
            stripped = source[4:]
            try:
                source = int(stripped)
            except ValueError:
                raise ScanariumError('SE_VALUE', 'Failed to parse "{stripped}"'
                                     ' of source "{source}" to number',
                                     {'stripped': stripped,
                                      'source': source})
        camera = cv2.VideoCapture(source)

        if not camera.isOpened():
            raise ScanariumError('SE_CAP_NOT_OPEN',
                                 'Failed to open camera "{source}"',
                                 {'source': source})

        # To avoid having to use external programs for basic camera setup, we
        # set the most basic properties right within Scanarium
        set_camera_property(scanarium, camera, cv2.CAP_PROP_FRAME_WIDTH,
                            'width')
        set_camera_property(scanarium, camera, cv2.CAP_PROP_FRAME_HEIGHT,
                            'height')

        # Since we do not necessarily need all images, but much rather want to
        # arrive at the most recent image quickly, we keep buffers as small as
        # we can, so we need to skip over as few buffered images as possible.
        # But as minimizing buffers makes some image pipelines re-initialize
        # themselves, which might throw cameras off, we only minimize buffers
        # if the configuration allows it.
        if scanarium.get_config('scan', 'minimize_buffers', 'boolean'):
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            camera.set(cv2.CAP_PROP_GSTREAMER_QUEUE_LENGTH, 1)

        delay = scanarium.get_config('scan', 'delay', allow_empty=True,
                                     kind='float')
        if delay:
            camera.grab()
            time.sleep(delay)
    elif camera_type == 'STATIC-IMAGE-CAMERA':
        camera = camera_type
    else:
        raise ScanariumError('SE_CAM_TYPE_UNKNOWN',
                             'Unknown camera type "{camera_type}"',
                             {'camera_type': camera_type})

    return camera


def close_camera(scanarium, camera):
    camera_type = get_camera_type(scanarium)
    if camera_type == 'PROPER-CAMERA':
        camera.release()
    elif camera_type == 'STATIC-IMAGE-CAMERA':
        # Camera is static image, nothing to do
        pass
    else:
        raise ScanariumError('SE_CAM_TYPE_UNKNOWN',
                             'Unknown camera type "{camera_type}"',
                             {'camera_type': camera_type})


def set_camera_property(scanarium, cap, property, config_key):
    value = scanarium.get_config('scan', config_key, allow_empty=True,
                                 kind='int')
    if value is not None:
        cap.set(property, value)


def get_raw_image(scanarium, camera=None):
    manage_camera = camera is None
    if manage_camera:
        camera = open_camera(scanarium)

    camera_type = get_camera_type(scanarium)
    if camera_type == 'PROPER-CAMERA':
        success = True
        duration = -1
        min_duration = scanarium.get_config(
            'scan', 'minimum_grab_time', kind='float')
        while success and duration < min_duration:
            start = time.time()
            success = camera.grab()
            duration = time.time() - start

        if success:
            # Grabbing worked and duration is ok, so we try to retrieve
            success, image = camera.retrieve()

        if not success:
            # Either grabbing or retrieving failed. So we give up.
            raise ScanariumError('SE_SCAN_NO_RAW_IMAGE',
                                 'Failed to retrieve image from camera')

    elif camera_type == 'STATIC-IMAGE-CAMERA':
        file_path = scanarium.get_config('scan', 'source')[6:]
        if os.path.isfile(file_path):
            image = get_raw_image_from_file(scanarium, file_path)
        else:
            raise ScanariumError('SE_SCAN_STATIC_SOURCE_MISSING',
                                 'The static source "{file}" does not exist',
                                 {'file': file_path})
    else:
        raise ScanariumError('SE_CAM_TYPE_UNKNOWN',
                             'Unknown camera type "{camera_type}"',
                             {'camera_type': camera_type})

    if manage_camera:
        close_camera(scanarium, camera)

    store_raw_image(scanarium, image)
    scanarium.debug_show_image('Raw image', image)

    min_width = scanarium.get_config('scan', 'min_raw_width_trip', kind='int')
    if image.shape[1] < min_width:
        raise ScanariumError(
            'SE_SCAN_IMAGE_TOO_SMALL',
            'Image is too small. Minimum width is {min_width} pixels',
            {'min_width': min_width})

    return image


def get_raw_image_from_file(scanarium, file_path):
    image = None
    format = scanarium.guess_image_format(file_path)
    log_raw_image(scanarium, format, file_path)

    if format is not None and \
            scanarium.get_config('scan', f'permit_file_type_{format}',
                                 kind='boolean', allow_missing=True):
        pipeline = scanarium.get_config('scan', f'pipeline_file_type_{format}',
                                        allow_missing=True, default='convert')
        image = run_get_raw_image_pipeline(scanarium, file_path, pipeline)

    if image is None:
        supported_formats = ', '.join(
            [key[17:].upper()
             for key in scanarium.get_config_keys('scan')
             if key.startswith('permit_file_type_') and scanarium.get_config(
                    'scan', key, kind='boolean')])
        raise ScanariumError(
            'SE_SCAN_STATIC_UNREADABLE_IMAGE_TYPE',
            'Only {supported_formats} files are supported.',
            {'supported_formats': supported_formats})

    return image


def run_get_raw_image_pipeline(scanarium, file_path, pipeline):
    image = None
    dpi = 150
    quality = 75

    if pipeline == 'native':
        image = cv2.imread(file_path)
    else:
        with tempfile.TemporaryDirectory(prefix='scanarium-conv-') as dir:
            converted_path_base = os.path.join(dir, 'converted')
            converted_path = converted_path_base + '.jpg'

            if pipeline == 'pdftoppm':
                command = [scanarium.get_config('programs',
                                                'pdftoppm_untrusted'),
                           '-jpeg',
                           '-singlefile',
                           '-r', str(dpi),
                           '-jpegopt', f'quality={quality}',
                           file_path,
                           converted_path_base]
            elif pipeline == 'convert':
                command = [scanarium.get_config('programs',
                                                'convert_untrusted'),
                           '-units', 'pixelsperinch',
                           '-background', 'white',
                           '-flatten',
                           '-density', str(dpi),
                           '-quality', str(quality),
                           file_path + '[0]',  # [0] is first page
                           converted_path]
            else:
                raise ScanariumError(
                    'SE_SCAN_UNKNOWN_PIPELINE',
                    'Unknown conversion pipeline \"{pipeline}\"',
                    {'pipeline': pipeline})

            try:
                scanarium.run(command)
            except OSError:
                if scanarium.get_config('debug', 'fine_grained_errors',
                                        kind='boolean'):
                    raise ScanariumError(
                        'SE_PIPELINE_OS_ERROR',
                        'Server-side image processing failed')
                else:
                    raise create_error_pipeline()

            except ScanariumError as e:
                if e.code == 'SE_TIMEOUT':
                    if scanarium.get_config('debug', 'fine_grained_errors',
                                            kind='boolean'):
                        raise ScanariumError(
                            'SE_PIPELINE_TIMEOUT',
                            'Server-side image processing took too long')
                    else:
                        raise create_error_pipeline()
                elif e.code == 'SE_RETURN_VALUE':
                    if scanarium.get_config('debug', 'fine_grained_errors',
                                            kind='boolean'):
                        raise ScanariumError(
                            'SE_PIPELINE_RETURN_VALUE',
                            'Server-side image processing failed')
                    else:
                        raise create_error_pipeline()
                else:
                    raise e

            if os.path.isfile(converted_path):
                image = cv2.imread(converted_path)

    return image


def log_raw_image(scanarium, format, file_path):
    if scanarium.get_config('log', 'raw_image_files', kind='boolean'):
        try:
            file_base = f'raw-image-file.{format}'
            log_filename = scanarium.get_log_filename(file_base)
            shutil.copy2(file_path, log_filename)
        except Exception:
            # Logging the file failed. There's not much that we can do
            # here, so we simply pass.
            pass


def store_raw_image(scanarium, image):
    global NEXT_RAW_IMAGE_STORE
    dir_path = scanarium.get_config(
        'scan', 'raw_image_directory', allow_empty=True)
    if dir_path is not None:
        now = time.time()
        if now >= NEXT_RAW_IMAGE_STORE:
            file_path = os.path.join(dir_path, '%f.png' % (now))
            os.makedirs(dir_path, exist_ok=True)
            cv2.imwrite(file_path, image)
            NEXT_RAW_IMAGE_STORE = now + scanarium.get_config(
                'scan', 'raw_image_period', 'float')


def undistort_image(scanarium, image):
    ret = image
    param_file = scanarium.get_config(
        'scan', 'calibration_xml_file', allow_empty=True)
    if param_file:
        try:
            storage = cv2.FileStorage(param_file, cv2.FileStorage_READ)
            cam_matrix = storage.getNode('cameraMatrix').mat()
            dist_coeffs = storage.getNode('dist_coeffs').mat()
        except Exception:
            raise ScanariumError(
                'SE_LOAD_UNDISTORT',
                'Failed to load parameters for undistortion from '
                '\"{file_name}\"',
                {'file_name': param_file})

        height, width = image.shape[:2]
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
            cam_matrix, dist_coeffs, (width, height), 1)

        ret = cv2.undistort(ret, cam_matrix, dist_coeffs, None,
                            new_camera_matrix)
        scanarium.debug_show_image('Undistorted image', ret)
    return ret


def get_image(scanarium, camera=None):
    image = get_raw_image(scanarium, camera)
    (image, _) = scale_image_from_config(scanarium, image, 'raw')
    return undistort_image(scanarium, image)
