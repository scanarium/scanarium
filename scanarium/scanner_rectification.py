# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import random

import cv2
import numpy as np

from .ScanariumError import ScanariumError
from .scanner_util import prepare_image, apply_image_contrast


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
                        ratings=None, points=[]):
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

        for point in points:
            cv2.drawMarker(contours_image, point, colors.get('good'))

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

    debug_show_contours(scanarium, 'All contours', image, contours, hierarchy,
                        points=required_points)

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
                        hierarchy, ratings=ratings, points=required_points)
    debug_show_contours(scanarium, 'Rated approximations', image,
                        approximations, hierarchy, ratings=ratings,
                        points=required_points)

    return good_approx


def sort_points_assume_xy_mostly_aligned(points):
    # The following heuristics of classifying the 4 points is based on the
    # assumption that the rectangle is not distorted too much. So if the
    # camera angle is skew, it will fail.
    s = points.sum(axis=1)
    s_tl = points[np.argmin(s)]  # smallest sum, is top left
    s_br = points[np.argmax(s)]  # biggest sum, is bottom right

    d = np.diff(points, axis=1)
    s_tr = points[np.argmin(d)]  # smallest difference, is top right
    s_bl = points[np.argmax(d)]  # biggest difference, is bottom left

    return (s_tl, s_tr, s_br, s_bl)


def sort_points_assume_roughly_45_degrees(points):
    # We assume the picture is rotated roughly 45 degrees

    y_sort = points[:, 1].argsort()
    s_tl = points[y_sort[0]]  # smallest y, is top left
    s_br = points[y_sort[3]]  # largest y, is bottom_right

    # Of the remaining 2 points, pick the one with smaller x as bottom left,
    # and the other as top right.
    if points[y_sort[1]][0] < points[y_sort[2]][0]:
        s_bl = points[y_sort[1]]
        s_tr = points[y_sort[2]]
    else:
        s_tr = points[y_sort[1]]
        s_bl = points[y_sort[2]]

    return (s_tl, s_tr, s_br, s_bl)


def rectify_by_rect_points(scanarium, image, points):
    M = None
    for sort_function in [
        sort_points_assume_xy_mostly_aligned,
        sort_points_assume_roughly_45_degrees,
            ]:
        if M is None:
            (s_tl, s_tr, s_br, s_bl) = sort_function(points)

            source = np.array([s_tl, s_tr, s_br, s_bl], dtype="float32")

            # Computing minimal distances between points for sanity checking
            min_dist = min([distance(source[i], source[j])
                            for i in range(4) for j in range(i + 1, 4)])
            if min_dist > min(image.shape[0], image.shape[1]) * 0.1:
                # Points are sufficiently far apparent to be plausible

                d_w = int(max(distance(s_br, s_bl), distance(s_tr, s_tl))) - 1
                d_h = int(max(distance(s_tr, s_br), distance(s_tl, s_bl))) - 1

                dest = np.array([[0, 0], [d_w, 0], [d_w, d_h], [0, d_h]],
                                dtype="float32")

                M = cv2.getPerspectiveTransform(source, dest)

    if M is None:
        raise ScanariumError(
            'SE_SCAN_NO_APPROX',
            'Failed to find black bounding rectangle in image')

    image = cv2.warpPerspective(image, M, (d_w, d_h))
    scanarium.debug_show_image('Rectified image', image)
    return image


def rectify(scanarium, image, decreasingArea=True, required_points=[],
            yield_only_points=False):
    found_points_scaled_list = []
    (prepared_image, scale_factor) = prepare_image(scanarium, image)

    contrasts = [float(contrast.strip())
                 for contrast in
                 scanarium.get_config('scan', 'contrasts').split(',')]
    for contrast in contrasts:
        fully_prepared_image = apply_image_contrast(prepared_image, contrast)

        scanarium.debug_show_image(
            f'Prepared for detection (contrast: {contrast})',
            fully_prepared_image)

        required_points_scaled = [(int(point[0] * scale_factor),
                                   int(point[1] * scale_factor)
                                   ) for point in required_points]
        found_points_scaled = find_rect_points(
            scanarium, fully_prepared_image, decreasingArea,
            required_points_scaled)
        if found_points_scaled is not None:
            found_points_scaled_list.append(found_points_scaled)

    if not found_points_scaled_list:
        raise ScanariumError(
            'SE_SCAN_NO_APPROX',
            'Failed to find black bounding rectangle in image')

    found_points_scaled_list.sort(key=cv2.contourArea)
    best_found_points_scaled = found_points_scaled_list[0]
    best_found_points = (best_found_points_scaled / scale_factor)\
        .astype('float32')

    rectify_points = refine_corners(
        scanarium, prepared_image, best_found_points)

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

    inset_factor = 0.25  # 0.25 to make sure the points we're checking for are
    # within the QR code, even for 45° rotated images taken straight from top.
    inset_factor += 0.05  # Adding 0.05 to have some wiggle room.
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
