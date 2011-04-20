#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

import re
import hashlib

from thumbor.crypto import Crypto
from libthumbor import CryptoURL

def test_usage():
    key = "my-security-key"
    image = "s.glbimg.com/et/bb/f/original/2011/03/24/VN0JiwzmOw0b0lg.jpg"
    thumbor_crypto = Crypto(salt=key)

    thumbor_options = thumbor_crypto.encrypt(
        width=300,
        height=200,
        smart=True,
        fit_in=False,
        flip_horizontal=False,
        flip_vertical=False,
        halign='center',
        valign='middle',
        crop_left=0,
        crop_top=0,
        crop_right=0,
        crop_bottom=0,
        image=image
    )
    thumbor_url = "/%s/%s" % (thumbor_options, image)

    crypto = CryptoURL(key=key)

    url = crypto.generate(
        width=300,
        height=200,
        smart=True,
        image_url=image
    )

    assert url == thumbor_url

def test_thumbor_can_decrypt_lib_thumbor_generated_url():
    key = "my-security-key"
    image = "s.glbimg.com/et/bb/f/original/2011/03/24/VN0JiwzmOw0b0lg.jpg"
    thumbor_crypto = Crypto(salt=key)

    crypto = CryptoURL(key=key)

    url = crypto.generate(
        width=300,
        height=200,
        smart=True,
        image_url=image
    )

    reg = "/([^/]+)/(.+)"
    options = re.match(reg, url).groups()[0]

    decrypted_url = thumbor_crypto.decrypt(options)

    assert decrypted_url
    assert decrypted_url['height'] == 200
    assert decrypted_url['width'] == 300
    assert decrypted_url['smart']
    assert decrypted_url['image_hash'] == hashlib.md5(image).hexdigest()

