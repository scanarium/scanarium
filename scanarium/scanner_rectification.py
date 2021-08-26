# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import random

import cv2
import numpy as np

from .ScanariumError import ScanariumError
from .scanner_util import scale_image


def get_cv_major_version():
    return int(cv2.__version__.split('.', 1)[0])


def distance(pointA, pointB):
    return np.linalg.norm([pointA - pointB])


def add_text(image, text, x=2, y=5, color=None):
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = image.shape[0] / 1000

    position = (int(image.shape[1] * x / 100),
                int(image.shape[0] * y / 100))

    if color is None:
        color = (0, 255, 0)

    return cv2.putText(image, text, position, font, fontScale, color)


def debug_show_contours(scanarium, name, image, contours, hierarchy,
                        ratings=None):
    if scanarium.get_config('general', 'debug', 'boolean'):
        # The contours image should contain the dampened image and allow color
        contours_image = cv2.cvtColor((image * 0.3).astype('uint8'),
                                      cv2.COLOR_GRAY2BGR)

        colors = {
            'small': (0, 0, random.randint(200, 256)),
            'non-rect': (0, random.randint(100, 140), 255),
            'outside-point': (0, 255, random.randint(200, 256)),
            'good': (0, 255, 0),
            'other': (255, 128, 128)
            }

        count = len(ratings if ratings else contours)
        drawn = 0
        for i in range(count):
            if ratings:
                color = colors.get(ratings[i], colors['other'])
            else:
                color = (random.randint(0, 256), random.randint(0, 256),
                         random.randint(0, 256))
            if contours[i] is not None:
                cv2.drawContours(contours_image, contours, i, color, 2,
                                 cv2.LINE_8, hierarchy, 0)
                drawn += 1
        add_text(contours_image, f'Drawn contours: {drawn}')

        if ratings:
            y = 5
            for k, v in sorted(colors.items()):
                y += 5
                add_text(contours_image, k, x=2, y=y, color=v)

        scanarium.debug_show_image(name, contours_image)


def refine_corners(scanarium, prepared_image, points):
    window_size = scanarium.get_config('scan', 'corner_refinement_size', 'int')
    if window_size > 1:
        search_window = (window_size, window_size)

        iteration_bound = scanarium.get_config(
            'scan', 'corner_refinement_iteration_bound', 'int')
        accuracy = scanarium.get_config(
            'scan', 'corner_refinement_accuracy', 'float')
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT,
                    iteration_bound, accuracy)

        points = cv2.cornerSubPix(
            prepared_image, points, search_window, (-1, -1), criteria)

    return points.reshape(4, 2)


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


def find_rect_points(scanarium, image, decreasingArea=True,
                     required_points=[]):
    imageArea = image.shape[0] * image.shape[1]
    contour_min_area = imageArea / 25
    prepared_image = image

    canny_blur_size = scanarium.get_config('scan', 'canny_blur_size',
                                           kind='int')
    canny_threshold_1 = scanarium.get_config('scan', 'canny_threshold_1',
                                             kind='int')
    canny_threshold_2 = scanarium.get_config('scan', 'canny_threshold_2',
                                             kind='int')
    if canny_blur_size > 1:
        prepared_image = cv2.blur(
            prepared_image, (canny_blur_size, canny_blur_size))
    edges_image = cv2.Canny(prepared_image, canny_threshold_1,
                            canny_threshold_2)
    # When looking for contours that contain some QR code, RETR_LIST (below)
    # might not be most efficient, RETR_TREE might allow to optimize. But
    # RETR_LIST is simpler to use and quick enough for now.
    # todo: See if RETR_TREE performs better here.
    contours_result = cv2.findContours(edges_image, cv2.RETR_LIST,
                                       cv2.CHAIN_APPROX_NONE)

    if get_cv_major_version() >= 4:
        contours, hierarchy = contours_result
    else:
        # OpenCV <4 used to pass back the image as first element in the tuple.
        # So we get rid of that to transparently work on OpenCV 3.x
        _, contours, hierarchy = contours_result

    debug_show_contours(scanarium, 'All contours', image, contours, hierarchy)

    good_approx = None
    contours.sort(key=cv2.contourArea, reverse=decreasingArea)
    ratings = []
    approximations = []
    for contour in contours:
        if cv2.contourArea(contour) < contour_min_area:
            # Contour too small, so we skip this contour
            ratings.append('small')
            approximations.append(None)
            continue

        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        approximations.append(approx)

        if len(approx) == 4:
            # 4 points ... that looks should be turned into a rectangle

            if any(cv2.pointPolygonTest(approx, point, False) < 0
                   for point in required_points):
                # A required point is outside, so we skip this contour.
                ratings.append('outside-point')
                continue

            # The contour is big enough, looks like a rect, and contains all
            # required points. That's the contour to continue with.
            good_approx = approx
            ratings.append('good')
            break
        else:
            ratings.append('non-rect')

    debug_show_contours(scanarium, 'Rated contours', image, contours,
                        hierarchy, ratings=ratings)
    debug_show_contours(scanarium, 'Rated approximations', image,
                        approximations, hierarchy, ratings=ratings)

    return good_approx


def rectify_by_rect_points(scanarium, image, points):
    # The following heuristics of classifying the 4 points is based on the
    # assumption that the rectangle is not distorted too much. So if the
    # camera angle is skew, it will fail.
    s = points.sum(axis=1)
    s_tl = points[np.argmin(s)]  # smallest sum, is top left
    s_br = points[np.argmax(s)]  # biggest sum, is bottom right

    d = np.diff(points, axis=1)
    s_tr = points[np.argmin(d)]  # smallest difference, is top right
    s_bl = points[np.argmax(d)]  # biggest difference, is bottom left

    source = np.array([s_tl, s_tr, s_br, s_bl], dtype="float32")

    d_w = int(max(distance(s_br, s_bl), distance(s_tr, s_tl))) - 1
    d_h = int(max(distance(s_tr, s_br), distance(s_tl, s_bl))) - 1

    dest = np.array([[0, 0], [d_w, 0], [d_w, d_h], [0, d_h]], dtype="float32")

    M = cv2.getPerspectiveTransform(source, dest)
    image = cv2.warpPerspective(image, M, (d_w, d_h))
    scanarium.debug_show_image('Rectified image', image)
    return image


def rectify(scanarium, image, decreasingArea=True, required_points=[],
            yield_only_points=False):
    found_points_scaled = None
    contrasts = [float(contrast.strip())
                 for contrast in
                 scanarium.get_config('scan', 'contrasts').split(',')]
    for contrast in contrasts:
        if contrast and found_points_scaled is None:
            (prepared_image, scale_factor) = prepare_image(scanarium, image,
                                                           contrast)

            required_points_scaled = [(int(point[0] * scale_factor),
                                       int(point[1] * scale_factor)
                                       ) for point in required_points]
            found_points_scaled = find_rect_points(
                scanarium, prepared_image, decreasingArea,
                required_points_scaled)

    if found_points_scaled is None:
        raise ScanariumError(
            'SE_SCAN_NO_APPROX',
            'Failed to find black bounding rectangle in image')

    found_points = (found_points_scaled / scale_factor).astype('float32')

    rectify_points = refine_corners(scanarium, prepared_image, found_points)

    if yield_only_points:
        ret = rectify_points
    else:
        # Now rectifying using the original (!) image.
        ret = rectify_by_rect_points(scanarium, image, rectify_points)
    return ret


def rectify_to_biggest_rect(scanarium, image, yield_only_points=False):
    return rectify(scanarium, image, decreasingArea=True,
                   yield_only_points=yield_only_points)


def rectify_to_qr_parent_rect(scanarium, image, qr_rect,
                              yield_only_points=False):
    def qr_rect_point(x_factor, y_factor):
        return (qr_rect.left + x_factor * qr_rect.width,
                qr_rect.top + y_factor * qr_rect.height)

    inset_factor = 0.2
    top_left_inset = qr_rect_point(inset_factor, inset_factor)
    top_right_inset = qr_rect_point(1. - inset_factor, inset_factor)
    bottom_left_inset = qr_rect_point(inset_factor, 1. - inset_factor)
    bottom_right_inset = qr_rect_point(1. - inset_factor, 1. - inset_factor)

    required_points = [
        top_left_inset,
        top_right_inset,
        bottom_left_inset,
        bottom_right_inset,
    ]

    return rectify(scanarium, image, decreasingArea=False,
                   required_points=required_points,
                   yield_only_points=yield_only_points)
