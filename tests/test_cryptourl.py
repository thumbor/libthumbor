#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

'''libthumbor cryptography tests'''
from unittest import TestCase

from thumbor.crypto import Crypto

from libthumbor.crypto import CryptoURL

IMAGE_URL = 'my.server.com/some/path/to/image.jpg'
KEY = 'my-security-key'

def decrypt_in_thumbor(url):
    '''Uses thumbor to decrypt libthumbor's encrypted URL'''
    encrypted = url.split('/')[1]
    crypto = Crypto(KEY)
    return crypto.decrypt(encrypted)

def test_decryption1():
    '''test_decryption1
    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 300
        And a height of 200
    When
        I ask my library for an encrypted URL
    Then
        I get
        '/l42l54VqaV_J-EcB5quNMP6CnsN9BX7htrh-QbPuDv0C7adUXX7LTo6DHm_woJtZ/my.server.com/some/path/to/image.jpg'
        as url
    '''
    crypto = CryptoURL(KEY)
    url = crypto.generate(image_url=IMAGE_URL, width=300, height=200)

    assert url == '/l42l54VqaV_J-EcB5quNMP6CnsN9BX7htrh-QbPuDv0C7adUXX7' + \
                  'LTo6DHm_woJtZ/my.server.com/some/path/to/image.jpg'

def test_decription2():
    '''test_decription2
    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 300
        And a height of 200
    When
        I ask my library for an encrypted URL
        And I call the aforementioned 'decrypt_in_thumbor' method
    Then
        I get a decrypted dictionary that contains the following:
            horizontal_flip = False
            vertical_flip = False
            smart = False
            fit_in = False
            meta = False
            crop['left'] = 0
            crop['top'] = 0
            crop['right'] = 0
            crop['bottom'] = 0
            valign = "middle"
            halign = "center"
            width = 300
            height = 200
            image_hash = 84996242f65a4d864aceb125e1c4c5ba
    '''
    crypto = CryptoURL(KEY)
    url = crypto.generate(image_url=IMAGE_URL, width=300, height=200)
    decrypted = decrypt_in_thumbor(url)

    assert decrypted['horizontal_flip'] == False
    assert decrypted['vertical_flip'] == False
    assert decrypted['smart'] == False
    assert decrypted['fit_in'] == False
    assert decrypted['meta'] == False
    assert decrypted['crop']['left'] == 0
    assert decrypted['crop']['top'] == 0
    assert decrypted['crop']['right'] == 0
    assert decrypted['crop']['bottom'] == 0
    assert decrypted['valign'] == "middle"
    assert decrypted['halign'] == "center"
    assert decrypted['width'] == 300
    assert decrypted['height'] == 200
    assert decrypted['image_hash'] == '84996242f65a4d864aceb125e1c4c5ba'

def test_decryption3():
    '''test_decryption3
    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And the meta flag
    When
        I ask my library for an encrypted URL
        And I call the aforementioned 'decrypt_in_thumbor' method
    Then
        I get a decrypted dictionary that contains the following:
            meta = True
            image_hash = 84996242f65a4d864aceb125e1c4c5ba
    '''

    crypto = CryptoURL(KEY)
    url = crypto.generate(image_url=IMAGE_URL, meta=True)
    decrypted = decrypt_in_thumbor(url)

    assert decrypted['meta'] == True
    assert decrypted['image_hash'] == '84996242f65a4d864aceb125e1c4c5ba'

def test_decryption_fit_in():
    '''test_decryption_fit_in
    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And the fit-in flag
    When
        I ask my library for an encrypted URL
        And I call the aforementioned 'decrypt_in_thumbor' method
    Then
        I get a decrypted dictionary that contains the following:
            fit-in = True
            image_hash = 84996242f65a4d864aceb125e1c4c5ba
    '''

    crypto = CryptoURL(KEY)
    url = crypto.generate(image_url=IMAGE_URL, fit_in=True)
    decrypted = decrypt_in_thumbor(url)

    assert decrypted['fit_in'] == True
    assert decrypted['image_hash'] == '84996242f65a4d864aceb125e1c4c5ba'

def test_decryption4():
    '''test_decryption4
    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And the smart flag
    When
        I ask my library for an encrypted URL
        And I call the aforementioned 'decrypt_in_thumbor' method
    Then
        I get a decrypted dictionary that contains the following:
            smart = True
            image_hash = 84996242f65a4d864aceb125e1c4c5ba
    '''

    crypto = CryptoURL(KEY)
    url = crypto.generate(image_url=IMAGE_URL, smart=True)
    decrypted = decrypt_in_thumbor(url)

    assert decrypted['smart'] == True
    assert decrypted['image_hash'] == '84996242f65a4d864aceb125e1c4c5ba'

def test_decryption5():
    '''test_decryption5
    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And the flip flag
    When
        I ask my library for an encrypted URL
        And I call the aforementioned 'decrypt_in_thumbor' method
    Then
        I get a decrypted dictionary that contains the following:
            flip_horizontally = True
            image_hash = 84996242f65a4d864aceb125e1c4c5ba
    '''

    crypto = CryptoURL(KEY)
    url = crypto.generate(image_url=IMAGE_URL, flip=True)
    decrypted = decrypt_in_thumbor(url)

    assert decrypted['horizontal_flip'] == True
    assert decrypted['image_hash'] == '84996242f65a4d864aceb125e1c4c5ba'

def test_decryption6():
    '''test_decryption6
    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And the flop flag
    When
        I ask my library for an encrypted URL
        And I call the aforementioned 'decrypt_in_thumbor' method
    Then
        I get a decrypted dictionary that contains the following:
            flip_vertically = True
            image_hash = 84996242f65a4d864aceb125e1c4c5ba
    '''

    crypto = CryptoURL(KEY)
    url = crypto.generate(image_url=IMAGE_URL, flop=True)
    decrypted = decrypt_in_thumbor(url)

    assert decrypted['vertical_flip'] == True
    assert decrypted['image_hash'] == '84996242f65a4d864aceb125e1c4c5ba'

def test_decryption7():
    '''test_decryption7
    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And the horizontal alignment of 'right'
    When
        I ask my library for an encrypted URL
        And I call the aforementioned 'decrypt_in_thumbor' method
    Then
        I get a decrypted dictionary that contains the following:
            halign = 'right'
            image_hash = 84996242f65a4d864aceb125e1c4c5ba
    '''

    crypto = CryptoURL(KEY)
    url = crypto.generate(image_url=IMAGE_URL, halign='right')
    decrypted = decrypt_in_thumbor(url)

    assert decrypted['halign'] == 'right'
    assert decrypted['image_hash'] == '84996242f65a4d864aceb125e1c4c5ba'

def test_decryption8():
    '''test_decryption8
    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And the vertical alignment of 'top'
    When
        I ask my library for an encrypted URL
        And I call the aforementioned 'decrypt_in_thumbor' method
    Then
        I get a decrypted dictionary that contains the following:
            valign = 'top'
            image_hash = 84996242f65a4d864aceb125e1c4c5ba
    '''

    crypto = CryptoURL(KEY)
    url = crypto.generate(image_url=IMAGE_URL, valign='top')
    decrypted = decrypt_in_thumbor(url)

    assert decrypted['valign'] == 'top'
    assert decrypted['image_hash'] == '84996242f65a4d864aceb125e1c4c5ba'

def test_decryption9():
    '''test_decryption9
    Given
        A security key of 'my-security-key'
        And an image URL of "my.server.com/some/path/to/image.jpg"
        And a manual crop left-top point of (10, 20)
        And a manual crop right-bottom point of (30, 40)
    When
        I ask my library for an encrypted URL
        And I call the aforementioned 'decrypt_in_thumbor' method
    Then
        I get a decrypted dictionary that contains the following:
            crop['left'] = 10
            crop['top'] = 20
            crop['right'] = 30
            crop['bottom'] = 40
            image_hash = 84996242f65a4d864aceb125e1c4c5ba
    '''

    crypto = CryptoURL(KEY)
    url = crypto.generate(image_url=IMAGE_URL, crop=((10, 20), (30, 40)))
    decrypted = decrypt_in_thumbor(url)

    assert decrypted['crop']['left'] == 10
    assert decrypted['crop']['top'] == 20
    assert decrypted['crop']['right'] == 30
    assert decrypted['crop']['bottom'] == 40
    assert decrypted['image_hash'] == '84996242f65a4d864aceb125e1c4c5ba'


class GenerateWithUnsafeTestCase(TestCase):

    def setUp(self):
        self.crypto = CryptoURL(KEY)

    def test_should_pass_unsafe_to_generate_and_get_an_unsafe_url(self):
        url = self.crypto.generate(image_url=IMAGE_URL, crop=((10, 20), (30, 40)), unsafe=True)
        self.assertTrue(url.startswith('unsafe'), "url should starts with unsafe")

    def test_should_not_get_an_unsafe_url_when_unsafe_is_false(self):
        url = self.crypto.generate(image_url=IMAGE_URL, crop=((10, 20), (30, 40)), unsafe=False)
        self.assertFalse(url.startswith('unsafe'), "url should not starts with unsafe")
