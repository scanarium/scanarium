# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import cv2
import numpy as np


def scale_image(scanarium, image, description, scaled_height=None,
                scaled_width=None, trip_height=None, trip_width=None):
    scaled_image = image

    def get_scale_factor(shape, trip, scaled):
        factor = 1
        if trip is None:
            trip = scaled
        if trip is not None and shape > trip and scaled is not None:
            factor = scaled / shape
        return factor

    height_factor = get_scale_factor(
        image.shape[0], trip_height, scaled_height)
    width_factor = get_scale_factor(image.shape[1], trip_width, scaled_width)
    scale_factor = min(height_factor, width_factor)
    if scale_factor != 1:
        scaled_height = int(image.shape[0] * scale_factor)
        scaled_width = int(image.shape[1] * scale_factor)
        scaled_dimension = (scaled_width, scaled_height)
        scaled_image = cv2.resize(image, scaled_dimension, cv2.INTER_AREA)

    scanarium.debug_show_image(f'Scaled image ({description})', scaled_image)

    return (scaled_image, scale_factor)


def correct_image_brightness(scanarium, image):
    factor = scanarium.get_brightness_factor()
    if factor is not None:
        # This pipeline normalizes each pixel with respect to the maximal
        # brightness allowed in the max image.
        image = np.clip(image * factor, 0, 255).astype(np.uint8)

    return image


def prepare_image(scanarium, image, contrast=1):
    # If the picture is too big (E.g.: from a proper photo camera), edge
    # detection won't work reliably, as the sheet's contour will exhibit too
    # much detail and would get broken down into more than 4 segments. So we
    # scale too big images down. Note though that the scaled image is only
    # used for edge detection. Rectification happens on the original picture.
    (prepared_image, scale_factor) = scale_image(
        scanarium, image, 'preparation', scaled_height=1000, trip_height=1300)

    if contrast != 1:
        shift = - 127.5 * (contrast - 1)
        prepared_image = np.clip(
            prepared_image.astype(np.float32) * contrast + shift, 0, 255
        ).astype(np.uint8)

    prepared_image = cv2.cvtColor(prepared_image, cv2.COLOR_BGR2GRAY)
    prepared_image = correct_image_brightness(scanarium, prepared_image)

    scanarium.debug_show_image(
        f'Prepared for detection (contrast: {contrast})', prepared_image)

    return (prepared_image, scale_factor)


def scale_image_from_config(scanarium, image, kind):
    def get_config(key):
        return scanarium.get_config('scan', f'max_{kind}_{key}',
                                    kind='int', allow_empty=True)

    return scale_image(scanarium, image, kind,
                       scaled_height=get_config('height'),
                       scaled_width=get_config('width'),
                       trip_height=get_config('height_trip'),
                       trip_width=get_config('width_trip'),
                       )
