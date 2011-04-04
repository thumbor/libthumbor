#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# https://github.com/heynemann/libthumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

'''libthumbor URL composer tests'''

from thumbor.crypto import Crypto

from libthumbor.url import url_for

IMAGE_URL = 'my.server.com/some/path/to/image.jpg'
IMAGE_MD5 = '84996242f65a4d864aceb125e1c4c5ba'

def decrypt_in_thumbor(key, encrypted):
    '''Uses thumbor to decrypt libthumbor's encrypted URL'''
    crypto = Crypto(key)    
    return crypto.decrypt(encrypted)

def test_no_options_specified():
    '''test_no_options_specified
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
    When
        I ask my library for an URL
    Then
        I get "84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(image_url=IMAGE_URL)

    assert url == IMAGE_MD5, url

def test_url_raises_if_no_url():
    '''test_url_raises_if_no_url
    Given
        An image URL of "" or null
    When
        I ask my library for an URL
    Then
        I get an exception that says image URL is mandatory
    '''
    try:
        url_for()
    except RuntimeError, err:
        assert str(err) == 'The image_url argument is mandatory.'
        return True
    assert False, 'Should not have gotten this far'

