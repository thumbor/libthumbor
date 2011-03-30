#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# https://github.com/heynemann/libthumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

from libthumbor import CryptoURL

def test_usage():
    crypto = CryptoURL(key='my-security-key')

    url = crypto.generate(
        width=300,
        height=200,
        smart=True,
        image_url='s.glbimg.com/et/bb/f/original/2011/03/24/VN0JiwzmOw0b0lg.jpg'
    )

    assert url == "/mjFhjvFRAj7oAfr1UZuGLXXjEI9yKAoTkrDhF5xnXLeF6CSX6_ZPbpqlBE_AhwZT/s.glbimg.com/et/bb/f/original/2011/03/24/VN0JiwzmOw0b0lg.jpg"
