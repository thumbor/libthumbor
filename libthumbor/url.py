#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# https://github.com/heynemann/libthumbor/wiki

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

    if 'image_url' not in options:
        raise RuntimeError('The image_url argument is mandatory.')

    url_parts = []

    calculate_width_and_height(url_parts, options)

    halign = options.get('halign', 'center')
    valign = options.get('valign', 'middle')

    if not halign in AVAILABLE_HALIGN:
        raise ValueError('Only "left", "center" and "right" are' + \
                         ' valid values for horizontal alignment.')
    if not valign in AVAILABLE_VALIGN:
        raise ValueError('Only "top", "middle" and "bottom" are' + \
                         ' valid values for vertical alignment.')

    if halign != 'center':
        url_parts.append(halign)
    if valign != 'middle':
        url_parts.append(valign)

    if options.get('smart', False):
        url_parts.append('smart')

    image_hash = hashlib.md5(options['image_url']).hexdigest()
    url_parts.append(image_hash)

    return "/".join(url_parts)
