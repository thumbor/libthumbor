#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# https://github.com/heynemann/libthumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

from thumbor.crypto import Crypto
from libthumbor import CryptoURL

def test_usage():
    key = "my-security-key"
    image = "s.glbimg.com/et/bb/f/original/2011/03/24/VN0JiwzmOw0b0lg.jpg"
    thumbor_crypto = Crypto(salt=key)

    thumbor_options = thumbor_crypto.encrypt(
        300,
        200,
        True,
        False,
        False,
        'center',
        'middle',
        0, 0, 0, 0,
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
