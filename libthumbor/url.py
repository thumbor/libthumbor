#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

'''URL composer to create options-based URLs for thumbor encryption.'''

import hashlib

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
    image_hash = hashlib.md5(options['image_url']).hexdigest()
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
    if options.get('fit_in', None):
        url_parts.append('fit-in')

    calculate_width_and_height(url_parts, options)

    halign = options.get('halign', 'center')
    valign = options.get('valign', 'middle')

    if not halign in AVAILABLE_HALIGN:
        raise ValueError('Only "left", "center" and "right" are' +
                         ' valid values for horizontal alignment.')
    if not valign in AVAILABLE_VALIGN:
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
