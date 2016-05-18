#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

'''URL composer to create options-based URLs for thumbor encryption.'''

import hashlib
import re

from six import b

AVAILABLE_HALIGN = ['left', 'center', 'right']
AVAILABLE_VALIGN = ['top', 'middle', 'bottom']


def calculate_width_and_height(url_parts, options):
    '''Appends width and height information to url'''
    width = options.get('width', 0)
    has_width = width
    height = options.get('height', 0)
    has_height = height

    flip = options.get('flip', False)
    flop = options.get('flop', False)

    if flip:
        width = width * -1
    if flop:
        height = height * -1

    if not has_width and not has_height:
        if flip:
            width = "-0"
        if flop:
            height = "-0"

    if width or height:
        url_parts.append('%sx%s' % (width, height))


def url_for(**options):
    '''Returns the url for the specified options'''

    url_parts = get_url_parts(**options)
    image_hash = hashlib.md5(b(options['image_url'])).hexdigest()
    url_parts.append(image_hash)

    return "/".join(url_parts)


def unsafe_url(**options):
    '''Returns the unsafe url with the specified options'''

    return 'unsafe/%s' % plain_image_url(**options)


def plain_image_url(**options):
    url_parts = get_url_parts(**options)
    url_parts.append(options['image_url'])

    return '/'.join(url_parts)


def get_url_parts(**options):
    if 'image_url' not in options:
        raise ValueError('The image_url argument is mandatory.')

    url_parts = []

    if options.get('meta', False):
        url_parts.append('meta')

    trim = options.get('trim', None)
    if trim:
        bits = ['trim']
        if not isinstance(trim, bool):
            bits.append(trim[0] if trim[0] else '')
            if trim[1]:
                bits.append(str(trim[1]))
        url_parts.append(':'.join(bits))

    crop = options.get('crop', None)
    if crop:
        crop_left = crop[0][0]
        crop_top = crop[0][1]
        crop_right = crop[1][0]
        crop_bottom = crop[1][1]

        if crop_left > 0 or crop_top > 0 or crop_bottom > 0 or crop_right > 0:
            url_parts.append("%sx%s:%sx%s" % (
                crop_left,
                crop_top,
                crop_right,
                crop_bottom
            ))

    fit_in = False
    full_fit_in = False

    if options.get('fit_in', None):
        fit_in = True
        url_parts.append('fit-in')

    if options.get('full_fit_in', None):
        full_fit_in = True
        url_parts.append('full-fit-in')

    if options.get('adaptive_fit_in', None):
        fit_in = True
        url_parts.append('adaptive-fit-in')

    if options.get('adaptive_full_fit_in', None):
        full_fit_in = True
        url_parts.append('adaptive-full-fit-in')

    if (fit_in or full_fit_in) and not (options.get('width', None) or options.get('height', None)):
        raise ValueError('When using fit-in or full-fit-in, you must specify width and/or height.')

    calculate_width_and_height(url_parts, options)

    halign = options.get('halign', 'center')
    valign = options.get('valign', 'middle')

    if halign not in AVAILABLE_HALIGN:
        raise ValueError('Only "left", "center" and "right" are' +
                         ' valid values for horizontal alignment.')
    if valign not in AVAILABLE_VALIGN:
        raise ValueError('Only "top", "middle" and "bottom" are' +
                         ' valid values for vertical alignment.')

    if halign != 'center':
        url_parts.append(halign)
    if valign != 'middle':
        url_parts.append(valign)

    if options.get('smart', False):
        url_parts.append('smart')

    if options.get('filters', False):
        filters_string = ['filters']
        for filter_value in options['filters']:
            filters_string.append(filter_value)
        url_parts.append(':'.join(filters_string))

    return url_parts


class Url(object):

    unsafe_or_hash = r'(?:(?:(?P<unsafe>unsafe)|(?P<hash>.+?))/)?'
    debug = '(?:(?P<debug>debug)/)?'
    meta = '(?:(?P<meta>meta)/)?'
    trim = '(?:(?P<trim>trim(?::(?:top-left|bottom-right))?(?::\d+)?)/)?'
    crop = '(?:(?P<crop_left>\d+)x(?P<crop_top>\d+):(?P<crop_right>\d+)x(?P<crop_bottom>\d+)/)?'
    fit_in = '(?:(?P<adaptive>adaptive-)?(?P<full>full-)?(?P<fit_in>fit-in)/)?'
    dimensions = '(?:(?P<horizontal_flip>-)?(?P<width>(?:\d+|orig))?x(?P<vertical_flip>-)?(?P<height>(?:\d+|orig))?/)?'
    halign = r'(?:(?P<halign>left|right|center)/)?'
    valign = r'(?:(?P<valign>top|bottom|middle)/)?'
    smart = r'(?:(?P<smart>smart)/)?'
    filters = r'(?:filters:(?P<filters>.+?\))/)?'
    image = r'(?P<image>.+)'

    compiled_regex = None

    @classmethod
    def regex(cls, has_unsafe_or_hash=True):
        reg = ['/?']

        if has_unsafe_or_hash:
            reg.append(cls.unsafe_or_hash)
        reg.append(cls.debug)
        reg.append(cls.meta)
        reg.append(cls.trim)
        reg.append(cls.crop)
        reg.append(cls.fit_in)
        reg.append(cls.dimensions)
        reg.append(cls.halign)
        reg.append(cls.valign)
        reg.append(cls.smart)
        reg.append(cls.filters)
        reg.append(cls.image)

        return ''.join(reg)

    @classmethod
    def parse_decrypted(cls, url):
        if cls.compiled_regex:
            reg = cls.compiled_regex
        else:
            reg = cls.compiled_regex = re.compile(cls.regex(has_unsafe_or_hash=False))

        result = reg.match(url)

        if not result:
            return None

        result = result.groupdict()

        def int_or_0(value):
            return 0 if value is None else int(value)

        adaptive = (result.get('adaptive', '') or '').startswith('adaptive')
        full = (result.get('full', '') or '').startswith('full')

        values = {
            'debug': result['debug'] == 'debug',
            'meta': result['meta'] == 'meta',
            'trim': result['trim'],
            'crop': {
                'left': int_or_0(result['crop_left']),
                'top': int_or_0(result['crop_top']),
                'right': int_or_0(result['crop_right']),
                'bottom': int_or_0(result['crop_bottom'])
            },
            'adaptive': adaptive,
            'full': full,
            'fit_in': result['fit_in'] == 'fit-in',
            'width': result['width'] == 'orig' and 'orig' or int_or_0(result['width']),
            'height': result['height'] == 'orig' and 'orig' or int_or_0(result['height']),
            'horizontal_flip': result['horizontal_flip'] == '-',
            'vertical_flip': result['vertical_flip'] == '-',
            'halign': result['halign'] or 'center',
            'valign': result['valign'] or 'middle',
            'smart': result['smart'] == 'smart',
            'filters': result['filters'] or '',
            'image': 'image' in result and result['image'] or None
        }

        return values

    @classmethod  # NOQA
    def generate_options(cls,
                         debug=False,
                         width=0,
                         height=0,
                         smart=False,
                         meta=False,
                         trim=None,
                         adaptive=False,
                         full=False,
                         fit_in=False,
                         horizontal_flip=False,
                         vertical_flip=False,
                         halign='center',
                         valign='middle',
                         crop_left=None,
                         crop_top=None,
                         crop_right=None,
                         crop_bottom=None,
                         filters=None):

        url = []

        if debug:
            url.append('debug')

        if meta:
            url.append('meta')

        if trim:
            if isinstance(trim, bool):
                url.append('trim')
            else:
                url.append('trim:%s' % trim)

        crop = crop_left or crop_top or crop_right or crop_bottom
        if crop:
            url.append('%sx%s:%sx%s' % (
                crop_left,
                crop_top,
                crop_right,
                crop_bottom
            ))

        if fit_in:
            fit_ops = []
            if adaptive:
                fit_ops.append('adaptive')
            if full:
                fit_ops.append('full')
            fit_ops.append('fit-in')
            url.append('-'.join(fit_ops))

        if horizontal_flip:
            width = '-%s' % width
        if vertical_flip:
            height = '-%s' % height

        if width or height:
            url.append('%sx%s' % (width, height))

        if halign != 'center':
            url.append(halign)
        if valign != 'middle':
            url.append(valign)

        if smart:
            url.append('smart')

        if filters:
            url.append('filters:%s' % filters)

        return '/'.join(url)
