#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# https://github.com/heynemann/libthumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

import hashlib
import base64

try:
    from pyDes import *
    pyDesFound = True
except ImportError:
    pyDesFound = False

class CryptoURL(object):
    def __init__(self, key):
        if not pyDesFound:
            raise RuntimeError('pyDes could not be found, please install it before using libthumbor')
        self.key = key
        self.computed_key = (key * 24)[:24]

    def generate(self,
                 meta=False,
                 width=0,
                 height=0,
                 smart=False,
                 flip_horizontal=False,
                 flip_vertical=False,
                 halign='center',
                 valign='middle',
                 crop_left=0,
                 crop_top=0,
                 crop_right=0,
                 crop_bottom=0,
                 image_url=None):

        if not image_url:
            raise RuntimeError("The image cannot be null or empty.")

        if image_url.startswith('/'):
            image_url = image_url[1:]

        url_parts = []

        if meta:
            url_parts.append("meta")

        crop = crop_left or crop_top or crop_right or crop_bottom
        if crop:
            url_parts.append("%sx%s:%sx%s" % (
                crop_left, crop_top, crop_right, crop_bottom
            ))

        if width and height:
            url_parts.append("%sx%s" % (width, height))
        elif width:
            url_parts.append("%sx0" % width)
        elif height:
            url_parts.append("0x%s" % height)

        if halign != 'center':
            url_parts.append(halign)
        if valign != 'middle':
            url_parts.append(valign)

        if smart:
            url_parts.append('smart')

        image_hash = hashlib.md5(image_url).hexdigest()
        url_parts.append(image_hash)

        url = "/".join(url_parts)

        key = triple_des(self.computed_key,
                         CBC, 
                         '\0\0\0\0\0\0\0\0', 
                         pad=None, 
                         padmode=PAD_PKCS5)

        encrypted = base64.urlsafe_b64encode(key.encrypt(url))

        return '/%s/%s' % (encrypted, image_url)
