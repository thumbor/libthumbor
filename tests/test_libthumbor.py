#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

import re
import hashlib

from thumbor.crypto import Cryptor, Signer
from thumbor.url import Url

from libthumbor import CryptoURL

def test_usage():
    key = "my-security-key"
    image = "s.glbimg.com/et/bb/f/original/2011/03/24/VN0JiwzmOw0b0lg.jpg"
    thumbor_crypto = Cryptor(key)

    thumbor_options = thumbor_crypto.encrypt(
        width=300,
        height=200,
        smart=True,
        adaptive=False,
        full=False,
        fit_in=False,
        flip_horizontal=False,
        flip_vertical=False,
        halign='center',
        valign='middle',
        trim=None,
        crop_left=0,
        crop_top=0,
        crop_right=0,
        crop_bottom=0,
        filters=[],
        image=image
    )
    thumbor_url = "/%s/%s" % (thumbor_options, image)

    crypto = CryptoURL(key=key)

    url = crypto.generate(
        width=300,
        height=200,
        smart=True,
        image_url=image,
        old=True
    )

    assert url == thumbor_url

def test_usage_new_format():
    key = "my-security-key"
    image = "s.glbimg.com/et/bb/f/original/2011/03/24/VN0JiwzmOw0b0lg.jpg"

    thumbor_signer = Signer(key)
    thumbor_url = Url.generate_options(
        width=300,
        height=200,
        smart=True,
        adaptive=False,
        fit_in=False,
        horizontal_flip=False,
        vertical_flip=False,
        halign='center',
        valign='middle',
        crop_left=0,
        crop_top=0,
        crop_right=0,
        crop_bottom=0,
        filters=[]
    )
    thumbor_url = ('%s/%s' % (thumbor_url, image)).lstrip('/')
    thumbor_url = '/%s/%s' % (thumbor_signer.signature(thumbor_url), thumbor_url)

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
    thumbor_crypto = Cryptor(key)

    crypto = CryptoURL(key=key)

    url = crypto.generate(
        width=300,
        height=200,
        smart=True,
        image_url=image,
        old=True
    )

    reg = "/([^/]+)/(.+)"
    options = re.match(reg, url).groups()[0]

    decrypted_url = thumbor_crypto.decrypt(options)

    assert decrypted_url
    assert decrypted_url['height'] == 200
    assert decrypted_url['width'] == 300
    assert decrypted_url['smart']
    assert decrypted_url['image_hash'] == hashlib.md5(image).hexdigest()

def test_thumbor_can_decrypt_lib_thumbor_generated_url_new_format():
    key = "my-security-key"
    image = "s.glbimg.com/et/bb/f/original/2011/03/24/VN0JiwzmOw0b0lg.jpg"
    thumbor_signer = Signer(key)

    crypto = CryptoURL(key=key)

    url = crypto.generate(
        width=300,
        height=200,
        smart=True,
        image_url=image
    )

    reg = "/([^/]+)/(.+)"
    (signature, url) = re.match(reg, url).groups()

    assert thumbor_signer.validate(signature, url)
