#!/usr/bin/env python3
# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import copy
import os
import json
import locale
import logging
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import qrcode

import cv2
import numpy as np

SCANARIUM_DIR_ABS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCANARIUM_DIR_ABS)
from scanarium import Scanarium, ScanariumError
del sys.path[0]

logger = logging.getLogger(__name__)

COMMAND_LABEL_SCENE = 'scene'
PARAMETER_LABEL_ACTOR = 'actor'

SVG_DPI = 96  # We assume Inkscape >= 0.92 (otherwise, use 90 here)

BACKGROUND_COLOR = '#ffffff'
LIGHT_COLOR = '#c0c0c0'
DARK_COLOR = '#808080'
THICK_WIDTH = 0.75590551
THIN_WIDTH = THICK_WIDTH / 2

THIN_LIGHT = {
    'stroke': LIGHT_COLOR,
    'stroke-width': THIN_WIDTH,
}
THICK_DARK = {
    'stroke': DARK_COLOR,
    'stroke-width': THICK_WIDTH,
}
THICK_DARK_FILLED = {
    'stroke': DARK_COLOR,
    'stroke-width': THICK_WIDTH,
    'fill': BACKGROUND_COLOR,
}

SVG_VARIANT_SETTINGS = {
    '': {
        'layer-settings': {
            'Mask': THICK_DARK_FILLED,
            'Overlay': THIN_LIGHT,
        },
    },
    'Detailed': {
        'layer-settings': {
            'Mask': THICK_DARK_FILLED,
            'Overlay': THICK_DARK,
            'Detailed': THICK_DARK,
        },
    }
}
SVG_VARIANTS = [key for key in SVG_VARIANT_SETTINGS.keys() if key]

LATEST_DECORATION_VERSION = None


def get_latest_decoration_version(scanarium):
    global LATEST_DECORATION_VERSION
    if LATEST_DECORATION_VERSION is None:
        best_version = None
        for item in os.listdir(scanarium.get_config_dir_abs()):
            match = re.match('^decoration-d-([0-9]*[1-9][0-9]*).svg$', item)
            if match:
                version = int(match.group(1).lstrip('0'))
                if best_version:
                    best_version = max(version, best_version)
                else:
                    best_version = version
        LATEST_DECORATION_VERSION = best_version
    return LATEST_DECORATION_VERSION


def run_inkscape(scanarium, arguments):
    command = [
        scanarium.get_config('programs', 'inkscape'),
        '--without-gui',
        '--export-text-to-path',
    ]
    command += arguments
    return scanarium.run(command)


def assert_directory(dir):
    if not os.path.isdir(dir):
        raise ScanariumError('E_NO_DIR', 'Is not a directory "{file_name}"',
                             {'file_name': dir})


def root_attribute_to_px(tree, name):
    raw = tree.getroot().attrib.get(name)
    ret = 0
    if raw.endswith('mm'):
        ret = float(raw[:-2]) / 25.4 * SVG_DPI
    elif raw.endswitch('in'):
        ret = float(raw[:-2]) * SVG_DPI
    elif raw.endswitch('px'):
        ret = float(raw[:-2])
    else:
        ret = float(raw)
    return ret


def get_svg_contour_rect_stroke_width(tree):
    stroke_width = 0
    try:
        path = './/{http://www.w3.org/2000/svg}rect[@id="contour"]'
        contour = tree.find(path)
        for setting in contour.attrib.get('style', '').split(';'):
            k_raw, v_raw = setting.split(':', 1)
            if k_raw.strip() == 'stroke-width':
                stroke_width = float(v_raw.strip())
    except Exception:
        logging.exception('Failed to parse "stroke-width"')

    return stroke_width


def get_svg_export_area_param_contour_inner(scanarium, svg_path):
    # We want to determine the white inner area of the rect with id
    # `contour` in user coordinates. Ideally, Inkscape would allow to access
    # that directly. However, its `--query*` arguments only allow to get the
    # rect's /outer/ dimensions. But we need the rect's inner dimensions
    # (without border). So we have to compute that manually by moving the
    # rect's stroke-width inwards.
    #
    # (At this point we do not make up for scalings/rotations in the document
    # tree above the rect.)

    tree = ET.parse(svg_path)
    stroke_width = get_svg_contour_rect_stroke_width(tree)

    inkscape_args = [
        '--query-all',
        svg_path,
    ]

    x = None
    y_top = None
    width = None
    height = None
    element_sizes = run_inkscape(
        scanarium, inkscape_args)['stdout'].split('\n')
    for element_size in element_sizes:
        if x is None or element_size.startswith('contour,'):
            # We're at either the first element (ie.: page), or the contour
            x, y_top, width, height = map(float, element_size.split(',')[1:])

    # When querying through Inkscape (as above), svg uses the top-left corner
    # as origin (as SVG does), but for `--export-area` it expects the
    # bottom-left corner as origin. So we need to re-compute the y from the
    # paper's bottom edge.
    paper_height = root_attribute_to_px(tree, 'height')
    y_bottom = paper_height - y_top - height

    # And as Inkscape reports the rect's outer coordinates, but we need the
    # inner coordinates (as that is what we extract when scanning a user
    # picture) we need to move the stroke-width inwards.
    return locale.format_string('%f:%f:%f:%f', (
        (x + stroke_width),
        (y_bottom + stroke_width),
        (x + width - stroke_width),
        (y_bottom + height - stroke_width),
    ))


def generate_adapted_mask_source(scanarium, tree, target, adapt_stroke_width):
    offset = 0
    if adapt_stroke_width:
        offset = scanarium.get_config('mask', 'stroke_offset', 'float')
    color = scanarium.get_config('mask', 'stroke_color', allow_empty=True)

    def adapt_style_element(style_element):
        if ':' in style_element:
            key, value = [s.strip() for s in style_element.split(':', 1)]
            new_value = value

            if offset and key == 'stroke-width':
                new_value = float(value) + offset
            elif color and key == 'stroke':
                new_value = color

            if value != new_value:
                style_element = f'{key}:{new_value}'

        return style_element

    def adapt_style(style):
        return ';'.join([adapt_style_element(style_element)
                         for style_element in style.split(';')])

    for element in tree.findall('.//*[@id="Mask"]//'):
        style = element.get('style')
        if style:
            element.set('style', adapt_style(style))
    tree.write(target)


def regenerate_mask_variant(
        scanarium, dir, scene, name, decoration_version, force,
        variant_name='', adapt_stroke_width=True):
    (tree, sources) = generate_full_svg_tree(
        scanarium, dir, name, decoration_version)

    target = scanarium.get_versioned_filename(
        dir, f'{name}-mask-{variant_name}', 'png', decoration_version)
    adapted_source = target[:-4] + '.svg'

    if scanarium.file_needs_update(adapted_source, sources, force):
        variant = ''
        localizer = scanarium.get_localizer('fallback')
        show_only_variant(tree, variant)
        filter_svg_tree(scanarium, tree, scene, name, variant,
                        localizer, COMMAND_LABEL_SCENE, PARAMETER_LABEL_ACTOR,
                        decoration_version, '../..')
        generate_adapted_mask_source(scanarium, tree, adapted_source,
                                     adapt_stroke_width)

    if scanarium.file_needs_update(target, [adapted_source], force):
        dpi = scanarium.get_config('mask', 'dpi', kind='int')
        contour_area = get_svg_export_area_param_contour_inner(
            scanarium, adapted_source)
        inkscape_args = [
            '--export-id=Mask',
            '--export-id-only',
            f'--export-area={contour_area}',
            '--export-background=black',
            f'--export-dpi={dpi}',
            '--export-png=%s' % (target),
            adapted_source,
        ]
        run_inkscape(scanarium, inkscape_args)
    return target


def crop(file):
    image = cv2.imread(file, 0)
    y, x = image.nonzero()

    return {
        "x_min": int(np.min(x)),
        "x_max_inc": int(np.max(x)) + 1,
        "y_min": int(np.min(y)),
        "y_max_inc": int(np.max(y)) + 1,
        "width": image.shape[1],
        "height": image.shape[0],
        }


def regenerate_mask(scanarium, dir, scene, name, decoration_version, force):
    unadapted_mask_png = regenerate_mask_variant(
        scanarium, dir, scene, name, decoration_version, force,
        variant_name='unadapted', adapt_stroke_width=False)

    effective_mask_png = regenerate_mask_variant(
        scanarium, dir, scene, name, decoration_version, force,
        variant_name='effective', adapt_stroke_width=True)

    effective_mask_json = effective_mask_png.rsplit('.', 1)[0] + '.json'
    if scanarium.file_needs_update(
            effective_mask_json, [unadapted_mask_png], force):
        scanarium.dump_json(effective_mask_json, crop(unadapted_mask_png))


def read_keywords(dir, language):
    ret = []
    keywords_filename = os.path.join(dir, 'keywords', language + '.txt')
    if os.path.exists(keywords_filename):
        with open(keywords_filename, 'r') as file:
            ret = [word for word in re.split(r'\s+', file.read()) if word]
    else:
        keywords_filename = None
    return (ret, keywords_filename)


def get_enriched_metadata(scanarium, metadata={}):
    def get_conf(key):
        return scanarium.get_config('cgi:regenerate-static-content', key)

    ret = {
        'attribution_name': get_conf('attribution_name'),
        'attribution_url': get_conf('attribution_url'),
        'rights_url': get_conf('rights_url'),
        'license_name': get_conf('license_name'),
        'license_url': get_conf('license_url'),
        'copyright_year': get_conf('copyright_year'),
        }
    ret['copyright'] = f'Copyright (C) {ret["copyright_year"]}  ' \
        f'{ret["attribution_name"]}. {ret["attribution_url"]} This work is ' \
        f'licensed under {ret["license_name"]}. See {ret["license_url"]}'
    ret['creator_tool'] = ret['attribution_name']
    ret['label'] = ret['attribution_name']

    ret = scanarium.update_dict(ret, metadata)

    ret['title'] = ret['localized_parameter_with_variant']

    keywords = ['Scanarium']
    for key in [
            'localized_command',
            'coloring-page-l10n',
            'localized_parameter_with_variant'
            ]:
        if metadata[key]:
            keywords.append(metadata[key])
    keywords.reverse()
    keywords.extend(ret.get('keywords', []))
    ret['description'] = ' '.join(keywords)
    ret['keywords'] = ', '.join(keywords)

    return ret


def embed_metadata(scanarium, target, metadata):
    if scanarium.get_config('cgi:regenerate-static-content',
                            'embed_metadata', kind='boolean'):
        enriched_metadata = get_enriched_metadata(scanarium, metadata)

        scanarium.embed_metadata(target, enriched_metadata)


def generate_pdf(scanarium, dir, file, force, metadata={}):
    dpi = 150
    quality = 75
    svg_source = os.path.join(dir, file)
    pdf_name = None

    metadata['dpi'] = dpi

    formats = ['pdf']
    for format in ['png', 'jpg']:
        if scanarium.get_config('cgi:regenerate-static-content',
                                f'generate_{format}', kind='boolean'):
            formats.append(format)

    for format in formats:
        target = os.path.join(
            dir, file.rsplit('.', 1)[0] + '.' + format)
        target_tmp = target + '.tmp.' + format  # Appending format to make sure
        # `convert` and colleagues can figure out the expected file format
        if format in ['pdf', 'png']:
            source = svg_source
            if scanarium.file_needs_update(target, [source], force):
                inkscape_args = [
                    '--export-area-page',
                    f'--export-dpi={dpi}',
                    '--export-%s=%s' % (format, target_tmp),
                    ]
                if format == 'png':
                    inkscape_args.append('--export-background=white')

                inkscape_args.append(source)

                run_inkscape(scanarium, inkscape_args)
            if format == 'pdf':
                pdf_name = target
        else:
            source = os.path.join(dir, file.rsplit('.', 1)[0] + '.png')
            if not scanarium.get_config('cgi:regenerate-static-content',
                                        'generate_png', kind='boolean'):
                raise ScanariumError(
                    'SE_REGENERATE_NO_SOURCE_FOR_TARGET',
                    'You need to enable '
                    '`cgi:regenerate-static-content.generate_png` to generate '
                    'the target file {target_file}.',
                    {'source_file': source, 'target_file': target})
            if scanarium.file_needs_update(target, [source], force):
                command = [
                    scanarium.get_config('programs', 'convert'),
                    source,
                    '-units', 'pixelsperinch',
                    '-background', 'white',
                    '-flatten',
                    '-density', str(dpi),
                    '-quality', str(quality),
                    target_tmp
                    ]
                scanarium.run(command)
        if scanarium.file_needs_update(target, [source], force):
            embed_metadata(scanarium, target_tmp, metadata)
            shutil.move(target_tmp, target)
    return pdf_name


def register_svg_namespaces():
    namespaces = {
        '': 'http://www.w3.org/2000/svg',
        'cc': 'http://creativecommons.org/ns#',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
        'svg': 'http://www.w3.org/2000/svg',
        'xlink': 'http://www.w3.org/1999/xlink',
    }
    for k, v in namespaces.items():
        ET.register_namespace(k, v)


def abbreviate_qr_data(scanarium, data):
    prefix = ''
    mapping_specs = scanarium.get_config('qr-code', 'mappings',
                                         allow_empty=True)
    if mapping_specs:
        for mapping_spec in mapping_specs.split(','):
            if not prefix:
                mapping_parts = mapping_spec.split('@')
                prefix_candidate = mapping_parts[0].strip()
                if len(mapping_parts) == 1:
                    prefix = prefix_candidate
                else:
                    file = mapping_parts[1].strip()
                    if file.startswith('%CONF_DIR%'):
                        file = os.path.join(scanarium.get_config_dir_abs(),
                                            file[11:])

                    with open(file, 'rt') as f:
                        code_map = json.load(f)

                    for k, v in code_map.items():
                        if not prefix and data == v:
                            prefix = prefix_candidate
                            data = k

    if prefix:
        data = prefix + data

    return data


def get_qr_path_string(scanarium, x, y, x_unit, y_unit, data):
    ret = ''

    # While qrcode allows to generate an SVG path element through
    # qrcode.image.svg.SvgPathImage, its's interface is not a close match
    # here. Also the unit setting is weird as dimensions get unconditionally
    # divided by 10. And finally, Python's qrcode libraries are not too active
    # these days, so we would not want to tie us too closely to any of
    # them. So we do the image -> svg transformation manually, as it's simple
    # enough, gives us more flexibility and untangles us from qrcode
    # internals.

    data = abbreviate_qr_data(scanarium, data)
    data_image = qrcode.make(data, box_size=1, border=0,
                             error_correction=qrcode.constants.ERROR_CORRECT_L)
    width = data_image.width
    height = data_image.height
    dot = f'h {x_unit:f} v {y_unit:f} h {-x_unit:f} Z'
    for j in range(0, height):
        for i in range(0, width):
            if data_image.getpixel((i, j)) == 0:
                ret += f'M {(x+i*x_unit):f} {(y-(height-j-1)*y_unit):f} {dot} '

    return ret


def expand_qr_pixel_to_qr_code(scanarium, element, data):
    x = float(element.get("x"))
    y = float(element.get("y"))
    x_unit = float(element.get("width"))
    y_unit = float(element.get("height"))

    element.tag = '{http://www.w3.org/2000/svg}path'
    element.set('d', get_qr_path_string(scanarium, x, y, x_unit, y_unit, data))

    for attrib in [
        "x",
        "y",
        "width",
        "height",
        "qr-pixel",
    ]:
        del(element.attrib[attrib])


def localize_command_parameter_variant(localizer, command, parameter, variant):
    def localize_parameter_with_alternative(key, value, alternative_keys=[]):
        ret = localizer.localize_parameter(key, value)
        for alternative_key in alternative_keys:
            if ret == value:
                ret = localizer.localize_parameter(alternative_key, ret)
        return ret

    localized_command = localize_parameter_with_alternative(
        'command_name', command, ['scene_name'])
    localized_parameter = localize_parameter_with_alternative(
        'parameter_name', parameter, ['actor_name', 'scene_name'])

    localized_variant = localizer.localize_parameter(
        'parameter_variant_name', variant)

    if variant:
        localized_parameter_with_variant = localizer.localize(
            '{parameter_name} ({parameter_variant_name})',
            {
                'parameter_name': localized_parameter,
                'parameter_variant_name': localized_variant
            })
    else:
        localized_parameter_with_variant = localized_parameter

    return (localized_command, localized_parameter, localized_variant,
            localized_parameter_with_variant)


def filter_svg_tree(scanarium, tree, command, parameter, variant, localizer,
                    command_label, parameter_label, decoration_version,
                    href_adjustment=None):
    (localized_command, localized_parameter, localized_variant,
     localized_parameter_with_variant) = localize_command_parameter_variant(
        localizer, command, parameter, variant)

    localized_command_label = localizer.localize_parameter(
        'command_label', command_label)
    localized_parameter_label = localizer.localize_parameter(
        'parameter_label', parameter_label)

    template_parameters = {
        'actor_name': localized_parameter,
        'command_label': localized_command_label,
        'command_name': localized_command,
        'command_name_raw': command,
        'parameter_label': localized_parameter_label,
        'parameter_name': localized_parameter,
        'parameter_with_variant_name': localized_parameter_with_variant,
        'parameter_name_raw': parameter,
        'scene_name': localized_command,
        'variant_name': localized_variant,
    }

    def filter_text(text):
        if text is not None:
            text = localizer.localize(text, template_parameters)
        return text

    for element in tree.iter():
        if element.tag == '{http://www.w3.org/2000/svg}g':
            if element.get('{http://www.inkscape.org/namespaces/inkscape}'
                           'groupmode') == 'layer':
                layer_name = extract_layer_name(element)
                style_enforcings = SVG_VARIANT_SETTINGS\
                    .get(variant, {})\
                    .get('layer-settings', {})\
                    .get(layer_name, {})

        element.text = filter_text(element.text)
        element.tail = filter_text(element.tail)
        for key in element.keys():
            value = filter_text(element.get(key))
            if key == 'style' and value is not None:
                style = {}
                for setting in value.split(';'):
                    setting = setting.strip()
                    if setting:
                        k, v = setting.split(':', 1)
                        style[k.strip()] = v
                for k, v in style_enforcings.items():
                    style[k] = str(v)
                value = ';'.join(':'.join(i) for i in style.items())
            if key == 'transform' and value is not None:
                if value.split('(', 1)[0] not in ['translate', 'rotate']:
                    raise ScanariumError('E_SVG_TRANSFORM_SCALE',
                                         'SVG uses unknown transformation')
            if key == '{http://www.w3.org/1999/xlink}href':
                if value and not value.startswith('/') and '://' not in value \
                        and href_adjustment:
                    value = href_adjustment + '/' + value
            element.set(key, value)

    for qr_element in list(tree.iter("{http://www.w3.org/2000/svg}rect")):
        qr_pixel = qr_element.attrib.get('qr-pixel', None)
        if qr_pixel is not None:
            if qr_pixel == command_label:
                qr_data = f'{command}:{parameter}:d_{decoration_version}'
                expand_qr_pixel_to_qr_code(scanarium, qr_element, qr_data)
            else:
                # We want to remove this qr-pixel, as it does not match the
                # needed type. But as it might be linked to other elements, we
                # instead make it invisible to avoid messing with the layout.
                #
                # As setting `visibility` does not seem to do the trick (at
                # least in Inkscape 0.92.3), we instead set opacity. This works
                # reliably in Inkscape.
                qr_element.set('style', 'opacity:0')


def extract_layers(tree):
    return tree.findall('./{http://www.w3.org/2000/svg}g')


def extract_layer_name(layer):
    name = layer.attrib.get('id')
    if name.startswith('layer'):
        name = layer.attrib.get(
            '{http://www.inkscape.org/namespaces/inkscape}label')
    return name


def extract_variant_from_layer(layer):
    variant = ''
    id = layer.attrib.get('id')
    if id in SVG_VARIANTS:
        variant = id
    else:
        label = layer.attrib.get(
            '{http://www.inkscape.org/namespaces/inkscape}label')
        if label in SVG_VARIANTS:
            variant = label
    return variant


def extract_variants(tree):
    ret = ['']
    for layer in extract_layers(tree):
        variant = extract_variant_from_layer(layer)
        if variant:
            ret.append(variant)
    return ret


def show_only_variant(tree, variant):
    for layer in extract_layers(tree):
        layer_variant = extract_variant_from_layer(layer)
        if layer_variant in SVG_VARIANTS:
            visible = layer_variant == variant
            display = 'inline' if visible else 'none'
            style = {}
            for setting in layer.attrib.get('style', '').split(';'):
                k, v = setting.split(':', 1)
                style[k.strip()] = v
            style['display'] = display
            layer.set('style', ';'.join(':'.join(i) for i in style.items()))


def append_svg_layers(base, addition):
    root = base.getroot()
    for layer in extract_layers(addition):
        root.append(layer)


def generate_full_svg_tree(scanarium, dir, parameter, decoration_version):
    undecorated_name = scanarium.get_versioned_filename(
        dir, parameter + '-undecorated', 'svg', decoration_version)
    decoration_name = scanarium.get_versioned_filename(
        scanarium.get_config_dir_abs(), 'decoration', 'svg',
        decoration_version)
    sources = [undecorated_name, decoration_name]
    register_svg_namespaces()
    tree = ET.parse(undecorated_name)
    append_svg_layers(tree, ET.parse(decoration_name))

    extra_decoration_name = scanarium.get_versioned_filename(
        os.path.join(dir, '..'), 'extra-decoration', 'svg', decoration_version)
    if os.path.isfile(extra_decoration_name):
        sources.append(extra_decoration_name)
        append_svg_layers(tree, ET.parse(extra_decoration_name))

    return (tree, sources)


def svg_variant_pipeline(scanarium, dir, command, parameter, variant, tree,
                         sources, is_actor, language, force, command_label,
                         parameter_label, decoration_version):
    localizer = scanarium.get_localizer(language)
    (localized_command, _, _, localized_parameter_with_variant) = \
        localize_command_parameter_variant(localizer, command, parameter,
                                           variant)

    base_name = scanarium.to_safe_filename(
        localized_parameter_with_variant) + '.svg'

    pdf_dir = os.path.join(dir, 'pdfs', language)
    os.makedirs(pdf_dir, exist_ok=True)
    full_svg_name = os.path.join(pdf_dir, base_name)

    (keywords, keywords_name) = read_keywords(dir, language)
    if keywords_name is not None:
        sources = sources + [keywords_name]

    metadata = {
        'language': language,
        'coloring-page-l10n':
            localizer.localize('coloring page') if is_actor else None,
        'command': command,
        'parameter': parameter,
        'variant': variant,
        'localized_command': localized_command if is_actor else None,
        'localized_parameter_with_variant':
            localized_parameter_with_variant if is_actor else None,
        'keywords': keywords,
        }

    if scanarium.file_needs_update(full_svg_name, sources, force):
        show_only_variant(tree, variant)
        filter_svg_tree(scanarium, tree, command, parameter, variant,
                        localizer, command_label, parameter_label,
                        decoration_version, '../..')
        embed_metadata(scanarium, tree, metadata)
        tree.write(full_svg_name)

    pdf_name = generate_pdf(scanarium, dir, full_svg_name, force,
                            metadata=metadata)

    if is_actor:
        scanarium.generate_thumbnail(dir, full_svg_name, force,
                                     level=['90%', '100%'])
    return pdf_name


def expand_languages(scanarium, language):
    if language is None or language == '':
        language = 'fallback'

    if language == 'all':
        l10n_dir = scanarium.get_localization_dir_abs()
        languages = ['fallback']
        for file in os.listdir(l10n_dir):
            if file.endswith('.json'):
                file = file[:-5]
                if len(file) == 2 and re.match('^[a-z]*$', file):
                    languages.append(file)
    else:
        languages = [language]
    return languages


def regenerate_pdf_actor_books_for_language(scanarium, dir, scene, language,
                                            pdfs, force):
    def keyer(pdf_name):
        return os.path.basename(pdf_name).rsplit('.', 1)[0]

    localizer = scanarium.get_localizer(language)
    target_dir = os.path.join(os.path.dirname(dir), 'pdfs', language)
    target_file = os.path.join(target_dir, scanarium.to_safe_filename(
            localizer.localize(
                'All {scene_name} coloring pages', {
                    'scene_name': scene})) + '.pdf')

    if scanarium.file_needs_update(target_file, pdfs, force):
        os.makedirs(target_dir, exist_ok=True)
        pdfs.sort(key=keyer)
        command = [scanarium.get_config('programs', 'pdfunite')]
        command += pdfs
        command.append(target_file)
        scanarium.run(command)


def regenerate_pdf_actor_books(scanarium, dir, scene, pdfs_by_language, force):
    for language, pdfs in pdfs_by_language.items():
        regenerate_pdf_actor_books_for_language(scanarium, dir, scene,
                                                language, pdfs, force)


def regenerate_masks(scanarium, dir, scene, name, force):
    latest_decoration_version = get_latest_decoration_version(scanarium)
    for decoration_version in range(1, latest_decoration_version + 1):
        build_version = decoration_version == latest_decoration_version
        if not build_version:
            undecorated_name = scanarium.get_versioned_filename(
                dir, name + '-undecorated', 'svg', decoration_version)
            build_version = os.path.isfile(undecorated_name)
        if build_version:
            regenerate_mask(scanarium, dir, scene, name, decoration_version,
                            force)


def regenerate_static_content_command_parameter(
        scanarium, dir, command, parameter, is_actor, language, force):
    command_label = COMMAND_LABEL_SCENE if is_actor else 'command'
    parameter_label = PARAMETER_LABEL_ACTOR if is_actor else 'parameter'
    logging.debug(f'Regenerating content for {command_label} "{command}", '
                  f'{parameter_label} "{parameter}" ...')

    assert_directory(dir)

    decoration_version = get_latest_decoration_version(scanarium)
    raw_tree, sources = generate_full_svg_tree(
        scanarium, dir, parameter, decoration_version)
    variants = extract_variants(raw_tree)
    variants.sort()
    pdfs_by_language = {}
    for language in expand_languages(scanarium, language):
        for variant in variants:
            variant_pdf_name = svg_variant_pipeline(
                scanarium, dir, command, parameter, variant,
                copy.deepcopy(raw_tree), sources, is_actor, language, force,
                command_label, parameter_label, decoration_version)
            pdfs_by_language[language] = pdfs_by_language.get(language, []) + \
                [variant_pdf_name]

    if is_actor:
        regenerate_masks(scanarium, dir, command, parameter, force)

    return variants, pdfs_by_language


def regenerate_static_content_command_parameters(
        scanarium, dir, command, parameter_arg, is_actor, language, force):
    parameters = os.listdir(dir) if parameter_arg is None else [parameter_arg]
    parameters.sort()
    command_variants = {}
    command_pdfs = {}
    for parameter in parameters:
        parameter_dir = os.path.join(dir, parameter)
        if os.path.isdir(parameter_dir):
            variants, pdfs_by_language = \
                regenerate_static_content_command_parameter(
                    scanarium, parameter_dir, command, parameter, is_actor,
                    language, force)
            if not os.path.exists(os.path.join(parameter_dir, 'hidden')):
                command_variants[parameter] = variants
                for pdf_language, pdfs in pdfs_by_language.items():
                    command_pdfs[pdf_language] = \
                        command_pdfs.get(pdf_language, []) + pdfs
    if is_actor and parameter_arg is None:
        scanarium.dump_json(os.path.join(dir, '..', 'actor-variants.json'),
                            command_variants)
        regenerate_pdf_actor_books(scanarium, dir, command, command_pdfs,
                                   force)


def regenerate_static_scene_content(scanarium, dir, force):
    scanarium.generate_thumbnail(dir, 'scene-bait.png', force)

    book_svg_file = os.path.join(scanarium.get_images_dir_abs(), 'book.svg')
    book_png_file = os.path.join(dir, 'scene-book.png')
    bait_png_file = os.path.join(dir, 'scene-bait.png')
    sources = [book_svg_file, bait_png_file]
    if scanarium.file_needs_update(book_png_file, sources, force):
        cwd_old = os.getcwd()
        os.chdir(dir)
        scanarium.run([scanarium.get_config('programs', 'convert'),
                       book_svg_file, book_png_file])
        os.chdir(cwd_old)

    scanarium.generate_thumbnail(dir, book_png_file, force)

    background_file = os.path.join(dir, 'background')
    background_jpg_file = os.path.join(dir, 'background.jpg')
    if os.path.islink(background_file) and \
            os.path.join(dir,
                         os.readlink(background_file)) == background_jpg_file:
        background_png_file = os.path.join(dir, 'background.png')
        if scanarium.file_needs_update(background_jpg_file,
                                       [background_png_file], force):
            scanarium.run([scanarium.get_config('programs', 'convert'),
                           background_png_file, background_jpg_file])


def regenerate_static_content_commands(
        scanarium, dir, command_arg, parameter, is_actor, language, force):
    scenes = []
    if os.path.isdir(dir):
        commands = os.listdir(dir) if command_arg is None else [command_arg]
        commands.sort()
        for command in commands:
            command_dir = os.path.join(dir, command)
            if os.path.isdir(command_dir):
                if is_actor:
                    regenerate_static_scene_content(scanarium, command_dir,
                                                    force)
                    command_dir = os.path.join(command_dir, 'actors')
                    scenes.append(command)
                if os.path.isdir(command_dir):
                    regenerate_static_content_command_parameters(
                        scanarium, command_dir, command, parameter, is_actor,
                        language, force)
        if is_actor and command_arg is None:
            file = os.path.join(scanarium.get_scenes_dir_abs(), 'scenes.json')
            scanarium.dump_json(file, scenes)


def regenerate_language_matrix(scanarium):
    logging.debug('Regenerating language matrix ...')
    l10ns = []
    data = {}
    data_file = 'localizations.json'
    l10n_dir = scanarium.get_localization_dir_abs()

    for l10n_file in os.listdir(l10n_dir):
        if l10n_file.endswith('.json') and l10n_file != data_file:
            l10ns.append(l10n_file[:-5])
    l10ns.sort()

    for ui_l10ns in l10ns:
        localizer = scanarium.get_localizer(ui_l10ns)
        for target_l10n in l10ns:
            data[f'{ui_l10ns}-{target_l10n}'] = localizer.localize_parameter(
                'language', target_l10n)
    data['localizations'] = l10ns
    scanarium.dump_json(os.path.join(l10n_dir, data_file), data)


def regenerate_static_images(scanarium, force):
    logging.debug('Regenerating static images ...')
    images_dir_abs = scanarium.get_images_dir_abs()
    book_svg_file = os.path.join(images_dir_abs, 'book.svg')
    book_png_file = os.path.join(images_dir_abs, 'book.png')

    if scanarium.file_needs_update(book_png_file, [book_svg_file], force):
        run_inkscape(scanarium, [
            '--export-png=%s' % (book_png_file),
            '--export-id=Book',
            '--export-id-only',
            '--export-area-page',
            book_svg_file
        ])

    scanarium.generate_thumbnail(images_dir_abs, book_png_file, force)


def regenerate_static_content(scanarium, command, parameter, language, force):
    for d in [
        {'dir': scanarium.get_commands_dir_abs(), 'is_actor': False},
        {'dir': scanarium.get_scenes_dir_abs(), 'is_actor': True},
    ]:
        regenerate_static_content_commands(
            scanarium, d['dir'], command, parameter, d['is_actor'], language,
            force)

    if not command and not parameter:
        regenerate_language_matrix(scanarium)
        regenerate_static_images(scanarium, force)


def register_arguments(scanarium, parser):
    parser.add_argument('--language',
                        help='Localize for the given language '
                        '(E.g.: \'de\' for German) Use `all` to localize for '
                        'all available languages', default='all')
    parser.add_argument('--force',
                        help='Regenerate all files, even if they are not'
                        'stale',
                        action='store_true')
    parser.add_argument('COMMAND', nargs='?',
                        help='Regenerate only the given command/scene')
    parser.add_argument('PARAMETER', nargs='?',
                        help='Regenerate only the given parameter/actor')


if __name__ == "__main__":
    scanarium = Scanarium()
    args = scanarium.handle_arguments('Regenerates all static content',
                                      register_arguments)
    scanarium.call_guarded(
        regenerate_static_content, args.COMMAND, args.PARAMETER,
        args.language, args.force)
