# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import cv2


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
