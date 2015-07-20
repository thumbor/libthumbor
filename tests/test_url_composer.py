#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

'''libthumbor URL composer tests'''
import sys
from unittest import TestCase

from six import PY3

if PY3:
    from thumbor_py3.crypto import Cryptor
else:
    from thumbor.crypto import Cryptor

from libthumbor.url import url_for
from libthumbor.url import unsafe_url

IMAGE_URL = 'my.server.com/some/path/to/image.jpg'
IMAGE_MD5 = '84996242f65a4d864aceb125e1c4c5ba'

def decrypt_in_thumbor(key, encrypted):
    '''Uses thumbor to decrypt libthumbor's encrypted URL'''
    crypto = Cryptor(key)
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
    except ValueError as err:
        assert str(err) == 'The image_url argument is mandatory.'
        return True
    assert False, 'Should not have gotten this far'

def test_url_width_height_1():
    '''test_url_width_height_1
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 300
    When
        I ask my library for an URL
    Then
        I get "300x0/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(width=300, image_url=IMAGE_URL)

    assert url == "300x0/84996242f65a4d864aceb125e1c4c5ba", url

def test_url_width_height_2():
    '''test_url_width_height_2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a height of 300
    When
        I ask my library for an URL
    Then
        I get "0x300/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(height=300, image_url=IMAGE_URL)

    assert url == "0x300/84996242f65a4d864aceb125e1c4c5ba", url

def test_url_width_height_3():
    '''test_url_width_height_3
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
    When
        I ask my library for an URL
    Then
        I get "200x300/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(width=200,
                  height=300,
                  image_url=IMAGE_URL)

    assert url == "200x300/84996242f65a4d864aceb125e1c4c5ba", url

def test_url_width_height_4():
    '''test_url_width_height_4
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of orig
    When
        I ask my library for an URL
    Then
        I get "origx0/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(width="orig", image_url=IMAGE_URL)

    assert url == "origx0/84996242f65a4d864aceb125e1c4c5ba", url

def test_url_width_height_5():
    '''test_url_width_height_5
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a height of orig
    When
        I ask my library for an URL
    Then
        I get "0xorig/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(height="orig", image_url=IMAGE_URL)

    assert url == "0xorig/84996242f65a4d864aceb125e1c4c5ba", url

def test_url_width_height_6():
    '''test_url_width_height_6
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 100
        And a height of orig
    When
        I ask my library for an URL
    Then
        I get "100xorig/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(width=100, height="orig", image_url=IMAGE_URL)

    assert url == "100xorig/84996242f65a4d864aceb125e1c4c5ba", url

def test_url_width_height_7():
    '''test_url_width_height_7
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a height of 100
        And a width of orig
    When
        I ask my library for an URL
    Then
        I get "origx100/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(width="orig", height=100, image_url=IMAGE_URL)

    assert url == "origx100/84996242f65a4d864aceb125e1c4c5ba", url

def test_url_width_height_8():
    '''test_url_width_height_8
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a height of orig
        And a width of orig
    When
        I ask my library for an URL
    Then
        I get "origxorig/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(width="orig", height="orig", image_url=IMAGE_URL)

    assert url == "origxorig/84996242f65a4d864aceb125e1c4c5ba", url

def test_smart_url():
    '''test_smart_url
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
        And the smart flag
    When
        I ask my library for an URL
    Then
        I get "200x300/smart/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(width=200,
                  height=300,
                  smart=True,
                  image_url=IMAGE_URL)

    assert url == "200x300/smart/84996242f65a4d864aceb125e1c4c5ba", url

def test_fit_in_url():
    '''test_fit_in_url
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
        And the fit-in flag
    When
        I ask my library for an URL
    Then
        I get "fit-in/200x300/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(width=200,
                  height=300,
                  fit_in=True,
                  image_url=IMAGE_URL)

    assert url == "fit-in/200x300/84996242f65a4d864aceb125e1c4c5ba", url

def test_adaptive_fit_in_url():
    '''test_adaptive_fit_in_url
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
        And the adaptive fit-in flag
    When
        I ask my library for an URL
    Then
        I get "adaptive-fit-in/200x300/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(width=200,
                  height=300,
                  adaptive_fit_in=True,
                  image_url=IMAGE_URL)

    assert url == "adaptive-fit-in/200x300/84996242f65a4d864aceb125e1c4c5ba", url

def test_fit_in_fails_if_no_width_supplied():
    try:
        url_for(fit_in=True, image_url=IMAGE_URL)
    except ValueError:
        err = sys.exc_info()[1]
        assert err is not None
    else:
        assert False, "Should not have gotten this far"

def test_full_fit_in_fails_if_no_width_supplied():
    try:
        url_for(full_fit_in=True, image_url=IMAGE_URL)
    except ValueError:
        err = sys.exc_info()[1]
        assert err is not None
    else:
        assert False, "Should not have gotten this far"

def test_adaptive_fit_in_fails_if_no_width_supplied():
    try:
        url_for(adaptive_fit_in=True, image_url=IMAGE_URL)
    except ValueError:
        err = sys.exc_info()[1]
        assert err is not None
    else:
        assert False, "Should not have gotten this far"

def test_adaptive_full_fit_in_fails_if_no_width_supplied():
    try:
        url_for(adaptive_full_fit_in=True, image_url=IMAGE_URL)
    except ValueError:
        err = sys.exc_info()[1]
        assert err is not None
    else:
        assert False, "Should not have gotten this far"

def test_full_fit_in_url():
    '''test_full_fit_in_url
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
        And the full-fit-in flag
    When
        I ask my library for an URL
    Then
        I get "full-fit-in/200x300/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(width=200,
                  height=300,
                  full_fit_in=True,
                  image_url=IMAGE_URL)

    assert url == "full-fit-in/200x300/84996242f65a4d864aceb125e1c4c5ba", url

def test_adaptive_full_fit_in_url():
    '''test_adaptive_full_fit_in_url
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
        And the adaptive full-fit-in flag
    When
        I ask my library for an URL
    Then
        I get "adaptive-full-fit-in/200x300/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(width=200,
                  height=300,
                  adaptive_full_fit_in=True,
                  image_url=IMAGE_URL)

    assert url == "adaptive-full-fit-in/200x300/84996242f65a4d864aceb125e1c4c5ba", url


def test_flip_1():
    '''test_flip_1
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And the flip flag
    When
        I ask my library for an URL
    Then
        I get "-0x0/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(flip=True,
                  image_url=IMAGE_URL)

    assert url == "-0x0/84996242f65a4d864aceb125e1c4c5ba", url

def test_flip_2():
    '''test_flip_2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And the flip flag
    When
        I ask my library for an URL
    Then
        I get "-200x0/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(flip=True,
                  width=200,
                  image_url=IMAGE_URL)

    assert url == "-200x0/84996242f65a4d864aceb125e1c4c5ba", url

def test_flop_1():
    '''test_flop_1
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And the flop flag
    When
        I ask my library for an URL
    Then
        I get "0x-0/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(flop=True,
                  image_url=IMAGE_URL)

    assert url == "0x-0/84996242f65a4d864aceb125e1c4c5ba", url

def test_flop_2():
    '''test_flop_2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a height of 200
        And the flop flag
    When
        I ask my library for an URL
    Then
        I get "0x-200/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(flop=True,
                  height=200,
                  image_url=IMAGE_URL)

    assert url == "0x-200/84996242f65a4d864aceb125e1c4c5ba", url

def test_flip_flop():
    '''test_flip_flop
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And the flip flag
        And the flop flag
    When
        I ask my library for an URL
    Then
        I get "-0x-0/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(flip=True,
                  flop=True,
                  image_url=IMAGE_URL)

    assert url == "-0x-0/84996242f65a4d864aceb125e1c4c5ba", url

def test_flip_flop2():
    '''test_flip_flop2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
        And the flip flag
        And the flop flag
    When
        I ask my library for an URL
    Then
        I get "-200x-300/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(flip=True,
                  flop=True,
                  width=200,
                  height=300,
                  image_url=IMAGE_URL)

    assert url == "-200x-300/84996242f65a4d864aceb125e1c4c5ba", url

def test_horizontal_alignment():
    '''test_horizontal_alignment
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'left' horizontal alignment option
    When
        I ask my library for an URL
    Then
        I get "left/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(halign='left',
                  image_url=IMAGE_URL)

    assert url == 'left/84996242f65a4d864aceb125e1c4c5ba', url

def test_horizontal_alignment2():
    '''test_horizontal_alignment2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'center' horizontal alignment option
    When
        I ask my library for an URL
    Then
        I get "84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(halign='center',
                  image_url=IMAGE_URL)

    assert url == '84996242f65a4d864aceb125e1c4c5ba', url

def test_vertical_alignment():
    '''test_vertical_alignment
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'top' vertical alignment option
    When
        I ask my library for an URL
    Then
        I get "top/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(valign='top',
                  image_url=IMAGE_URL)

    assert url == 'top/84996242f65a4d864aceb125e1c4c5ba', url

def test_vertical_alignment2():
    '''test_vertical_alignment2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'middle' vertical alignment option
    When
        I ask my library for an URL
    Then
        I get "84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(valign='middle',
                  image_url=IMAGE_URL)

    assert url == '84996242f65a4d864aceb125e1c4c5ba', url

def test_both_alignments():
    '''test_both_alignments
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'left' horizontal alignment option
        And a 'top' vertical alignment option
    When
        I ask my library for an URL
    Then
        I get "left/top/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(halign='left',
                  valign='top',
                  image_url=IMAGE_URL)

    assert url == 'left/top/84996242f65a4d864aceb125e1c4c5ba', url

def test_proper_haligns():
    '''test_proper_haligns'''
    try:
        url_for(halign='wrong', image_url=IMAGE_URL)
    except ValueError as err:
        assert str(err) == 'Only "left", "center" and "right"' + \
                           ' are valid values for horizontal alignment.'
        return True
    assert False, "Should not have gotten this far."

def test_proper_valigns():
    '''test_proper_haligns'''
    try:
        url_for(valign='wrong', image_url=IMAGE_URL)
    except ValueError as err:
        assert str(err) == 'Only "top", "middle" and "bottom"' + \
                           ' are valid values for vertical alignment.'
        return True
    assert False, "Should not have gotten this far."

def test_proper_meta():
    '''test_proper_meta
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'meta' flag
    When
        I ask my library for an URL
    Then
        I get "meta/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(meta=True,
                  image_url=IMAGE_URL)

    assert url == 'meta/84996242f65a4d864aceb125e1c4c5ba', url


def test_trim_standard():
    url = url_for(trim=True,
                  image_url=IMAGE_URL)
    assert url == 'trim/84996242f65a4d864aceb125e1c4c5ba', url


def test_trim_pixel_and_tolerance():
    url = url_for(trim=('bottom-right', 15),
                  image_url=IMAGE_URL)
    assert url == 'trim:bottom-right:15/84996242f65a4d864aceb125e1c4c5ba', url


def test_trim_pixel_only():
    url = url_for(trim=('top-left', None),
                  image_url=IMAGE_URL)
    assert url == 'trim:top-left/84996242f65a4d864aceb125e1c4c5ba', url


def test_trim_tolerance_only():
    url = url_for(trim=(None, 15),
                  image_url=IMAGE_URL)
    assert url == 'trim::15/84996242f65a4d864aceb125e1c4c5ba', url


def test_manual_crop_1():
    '''test_manual_crop_1
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a manual crop left-top point of (10, 20)
        And a manual crop right-bottom point of (30, 40)
    When
        I ask my library for an URL
    Then
        I get "10x20:30x40/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(crop=((10, 20), (30, 40)),
                  image_url=IMAGE_URL)

    assert url == '10x20:30x40/84996242f65a4d864aceb125e1c4c5ba', url

def test_manual_crop_2():
    '''test_manual_crop_2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a manual crop left-top point of (0, 0)
        And a manual crop right-bottom point of (0, 0)
    When
        I ask my library for an URL
    Then
        I get "84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(crop=((0, 0), (0, 0)),
                  image_url=IMAGE_URL)

    assert url == '84996242f65a4d864aceb125e1c4c5ba', url

def test_smart_after_alignments():
    '''test_smart_after_alignments
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'smart' flag
        And a 'left' horizontal alignment option
    When
        I ask my library for an URL
    Then
        I get "left/smart/84996242f65a4d864aceb125e1c4c5ba" as URL
    '''
    url = url_for(smart=True,
                  halign='left',
                  image_url=IMAGE_URL)

    assert url == 'left/smart/84996242f65a4d864aceb125e1c4c5ba', url


class UnsafeUrlTestCase(TestCase):

    def test_should_return_a_valid_unsafe_url_with_no_params(self):
        self.assertEqual('unsafe/%s' % IMAGE_URL, unsafe_url(image_url=IMAGE_URL))

    def test_should_return_an_unsafe_url_with_width_and_height(self):
        self.assertEqual('unsafe/100x140/%s' % IMAGE_URL, unsafe_url(image_url=IMAGE_URL, width=100, height=140))

    def test_should_return_an_unsafe_url_with_crop_and_smart(self):
        self.assertEqual('unsafe/100x140/smart/%s' % IMAGE_URL, unsafe_url(image_url=IMAGE_URL, width=100, height=140, smart=True))
