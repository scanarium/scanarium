# This file is part of Scanarium https://scanarium.com/ and licensed under the
# GNU Affero General Public License v3.0 (See LICENSE.md)
# SPDX-License-Identifier: AGPL-3.0-only

import collections.abc
import datetime
import logging
import os
import re
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

JPG_MAGIC = b'\xff\xd8\xff'
PDF_MAGIC = bytes('%PDF', 'utf-8')
PNG_MAGIC = bytes('PNG\r\n', 'utf-8')
HEIC_MAGIC = bytes('ftyp', 'utf-8')
HEIC_MAJOR_BRANDS = [bytes(brand, 'utf-8') for brand in [
    # See https://github.com/strukturag/libheif/issues/83
    'heic',
    'heim',
    'heis',
    'heix',
    'hevc',
    'hevm',
    'hevs',
    'mif1',
    'msf1',
]]


EXIFTOOL_METADATA_GROUPING = {
    'Copyright': {
        '': '@copyright',
        },
    'ExifIFD': {
        'UserComment': '@description',
        },
    'File': {
        'Comment': '@description',
        },
    'IFD0': {
        'Artist': '@attribution_name',
        'Copyright': '@copyright',
        'ImageDescription': '@description',
        'XResolution': '@dpi',
        'YResolution': '@dpi',
        },
    'IPTC': {
        'By-line': '@attribution_name',
        'Caption-Abstract': '@description',
        'CopyrightNotice': '@copyright',
        'Keywords': '@keywords',
        'OriginatingProgram': '@attribution_name',
        },
    'PDF': {
        'Keywords': '@keywords',
        'Author': '@attribution_name',
        'Producer': '@attribution_name',
        'Creator': '@attribution_name',
        'Title': '@title',
        'Subject': '@description',
        },
    'XMP-cc': {
        'attributionName': '@attribution_name',
        'attributionURL': '@attribution_url',
        'license': '@license_url',
        'morePermissions': '@rights_url',
        },
    'XMP-dc': {
        'creator': '@attribution_name',
        'description': '@description',
        'language': '@language',
        'rights': '@copyright',
        'title': '@title',
        },
    'XMP-exif': {
        'UserComment': '@description',
        },
    'XMP-tiff': {
        'Artist': '@attribution_name',
        'ImageDescription': '@description',
        'Software': '@attribution_name',
        },
    'XMP-photoshop': {
        'Credit': '@attribution_name',
        'Headline': '@description',
        },
    'XMP-plus': {
        'LicensorName': '@attribution_name',
        'LicensorURL': '@rights_url',
        },
    'XMP-pdf': {
        'Keywords': '@keywords',
        'Producer': '@attribution_name',
        'Creator': '@attribution_name',
        },
    'XMP-x': {
        'XMPToolkit': 'n/a',
        },
    'XMP-xmp': {
        'CreatorTool': '@creator_tool',
        'Label': '@label',
        'CreateDate': '@now_exif',
        },
    'XMP-xmpRights': {
        'Marked': 'True',
        'Owner': '@attribution_name',
        'UsageTerms': '@copyright',
        'WebStatement': '@rights_url',
        },
    }


def file_needs_update(destination, sources, force=False):
    ret = True
    if os.path.isfile(destination) and not force:
        ret = any(os.stat(destination).st_mtime < os.stat(source).st_mtime
                  for source in sources)
    return ret


def generate_thumbnail(scanarium, dir, file, force, levels=[]):
    source = os.path.join(dir, file)
    target = os.path.join(dir, file.rsplit('.', 1)[0] + '-thumb.jpg')

    if file_needs_update(target, [source], force):
        command = [scanarium.get_config('programs', 'convert'), source]
        if levels:
            command += ['-level', ','.join(level.strip() for level in levels)]
        command += [
            '-resize', '150x100',
            '-background', 'white',
            '-flatten',
            target
        ]
        scanarium.run(command)


def get_log_filename(scanarium, name, timestamped=True):
    full_dir = scanarium.get_log_dir_abs()
    if timestamped:
        now = get_now()
        date_dir = now.strftime(os.path.join('%Y', '%m', '%d'))
        full_dir = os.path.join(full_dir, date_dir)

        name = now.strftime('%H.%M.%S.%fZ-') + name

    os.makedirs(full_dir, exist_ok=True)
    full_file = os.path.join(full_dir, name)
    return full_file


def guess_image_format(file_path):
    guessed_type = None
    if os.path.getsize(file_path) >= 12:
        with open(file_path, mode='rb') as file:
            header = file.read(12)

            if header[0:3] == JPG_MAGIC:
                guessed_type = 'jpg'
            elif header[1:6] == PNG_MAGIC:
                guessed_type = 'png'
            elif header[0:4] == PDF_MAGIC:
                guessed_type = 'pdf'
            elif header[4:8] == HEIC_MAGIC and \
                    header[8:12] in HEIC_MAJOR_BRANDS:
                guessed_type = 'heic'

    return guessed_type


def to_safe_filename(name):
    ret = re.sub('[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789]+', '-', name).strip('-')
    if not ret:
        ret = 'unnamed'
    return ret


def update_dict(target, source, merge_lists=False):
    for key, value in source.items():
        if isinstance(value, collections.abc.Mapping):
            target[key] = update_dict(target.get(key, {}), value)
        elif merge_lists and isinstance(value, list) \
                and isinstance(target.get(key, 0), list):
            target[key] += value
        else:
            target[key] = value
    return target


def embed_metadata(scanarium, target, metadata={}):
    metadata = update_dict({
            'now_exif': get_now().strftime('%Y:%m:%d %H:%M:%SZ'),
            'now': get_now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }, metadata)
    if isinstance(target, ET.ElementTree):
        embed_metadata_svg_element_tree(scanarium, target, metadata)
    elif isinstance(target, str):
        embed_metadata_exiftool(scanarium, target, metadata)
    else:
        raise NotImplementedError(
            f'Unsupported type {type(target)} for metadata embedding')


def embed_metadata_svg_element_tree(scanarium, tree, metadata={}):
    def set_agent(element, kind, value):
        if value:
            child = ET.SubElement(element, f'dc:{kind}')
            agent = ET.SubElement(child, 'cc:Agent')
            title = ET.SubElement(agent, 'dc:title')
            title.text = value

    def add_subelement(element, kind, value):
        if value:
            child = ET.SubElement(element, kind)
            child.text = value.strip()

    def add_cc_resource(element, kind, what):
        ET.SubElement(
            element, f'cc:{kind}',
            attrib={'rdf:resource': f'http://creativecommons.org/ns#{what}'})

    for work in list(tree.iter("{http://creativecommons.org/ns#}Work")):
        if 'title' in metadata:
            for element in work.iter():
                if element.tag == '{http://purl.org/dc/elements/1.1/}title':
                    element.text = metadata['title']

        if 'keywords' in metadata:
            subject = ET.SubElement(work, 'dc:subject')
            bag = ET.SubElement(subject, 'rdf:Bag')
            for keyword in metadata['keywords'].split(','):
                add_subelement(bag, 'rdf:li', keyword)

        if 'license_url' in metadata:
            license_url = metadata['license_url']
            ET.SubElement(work, 'cc:license',
                          attrib={'rdf:resource': license_url})

            set_agent(work, 'rights', license_url)

        if 'attribution_name' in metadata:
            set_agent(work, 'creator', metadata['attribution_name'])

        if 'now' in metadata:
            add_subelement(work, 'dc:date', metadata['now'])

        if 'creator_tool' in metadata:
            set_agent(work, 'publisher', metadata['creator_tool'])

        if 'attribution_url' in metadata:
            add_subelement(work, 'dc:source', metadata['attribution_url'])

        if 'language' in metadata:
            add_subelement(work, 'dc:language', metadata['language'])

        if 'description' in metadata:
            add_subelement(work, 'dc:description', metadata['description'])

    if 'license_url' in metadata:
        license_url = metadata['license_url']
        if license_url == 'https://creativecommons.org/licenses/by-nc-sa/4.0/':
            for workParent in list(tree.iterfind(
                    '{http://www.w3.org/2000/svg}metadata/'
                    '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF')):
                license = ET.SubElement(workParent, 'cc:License',
                                        attrib={'rdf:about': license_url})
                add_cc_resource(license, 'permits', 'Reproduction')
                add_cc_resource(license, 'permits', 'Distribution')
                add_cc_resource(license, 'permits', 'DerivativeWorks')
                add_cc_resource(license, 'requires', 'Notice')
                add_cc_resource(license, 'requires', 'Attribution')
                add_cc_resource(license, 'requires', 'ShareAlike')
                add_cc_resource(license, 'prohibits', 'CommercialUse')


def embed_metadata_exiftool(scanarium, filename, metadata={}):
    command = [
        scanarium.get_config('programs', 'exiftool'),
        '-overwrite_original',
        '-all:all=',
        ]

    for group, kvs in EXIFTOOL_METADATA_GROUPING.items():
        for k, v in kvs.items():
            param = '-' + group
            if k:
                param += ':' + k

            if v:
                if v[0] == '@':
                    v = metadata.get(v[1:], '')
                if v:
                    command.append(f'{param}={v}')

    command.append(filename)
    scanarium.run(command)


def get_now():
    return datetime.datetime.now(tz=datetime.timezone.utc)


def get_timestamp_for_filename():
    return f'{get_now().timestamp():.3f}'


def get_versioned_filename(dir, file, suffix, decoration_version):
    return os.path.join(dir, f'{file}-d-{decoration_version}.{suffix}')


class Util(object):
    def __init__(self, scanarium):
        self._scanarium = scanarium

    def generate_thumbnail(self, scanarium, dir, file, force, level=[]):
        return generate_thumbnail(scanarium, dir, file, force, level)

    def file_needs_update(self, destination, sources, force=False):
        return file_needs_update(destination, sources, force)

    def get_log_filename(self, name, timestamped=True):
        return get_log_filename(self._scanarium, name, timestamped)

    def guess_image_format(self, file_path):
        return guess_image_format(file_path)

    def to_safe_filename(self, name):
        return to_safe_filename(name)

    def embed_metadata(self, scanarium, target, metadata):
        return embed_metadata(scanarium, target, metadata)

    def get_now(self):
        return get_now()

    def get_timestamp_for_filename(self):
        return get_timestamp_for_filename()

    def get_versioned_filename(self, dir, file, suffix, decoration_version):
        return get_versioned_filename(dir, file, suffix, decoration_version)

    def update_dict(self, target, source, merge_lists=False):
        return update_dict(target, source, merge_lists=merge_lists)
