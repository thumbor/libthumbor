# libthumbor - python extension to thumbor
# https://github.com/thumbor/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""libthumbor URL composer tests"""

import hashlib
from unittest import TestCase, mock

import pytest
from preggy import expect

from libthumbor.url import plain_image_url, unsafe_url, url_for

IMAGE_URL = "my.server.com/some/path/to/image.jpg"
IMAGE_MD5 = "84996242f65a4d864aceb125e1c4c5ba"


def test_no_options_specified():
    """test_no_options_specified
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
    When
        I ask my library for an URL
    Then
        I get "<image URL>" as URL
    """
    url = plain_image_url(image_url=IMAGE_URL)

    expect(url).to_equal(IMAGE_URL)


def test_url_for_is_deprecated():
    with pytest.warns(DeprecationWarning, match=r"url_for\(\) is deprecated") as record:
        url_for(image_url=IMAGE_URL)

    expect(record[0].filename).to_equal(__file__)


def test_url_for_replaces_the_image_url_with_its_md5():
    with pytest.warns(DeprecationWarning):
        url = url_for(width=300, image_url=IMAGE_URL)

    expect(url).to_equal(f"300x0/{IMAGE_MD5}")


def test_url_for_marks_md5_as_not_used_for_security():
    """test_url_for_marks_md5_as_not_used_for_security
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
    When
        I ask my library for an URL
    Then
        The image URL is hashed with md5 and usedforsecurity=False
    """
    with (
        mock.patch("libthumbor.url.hashlib.md5", wraps=hashlib.md5) as md5,
        pytest.warns(DeprecationWarning),
    ):
        url_for(image_url=IMAGE_URL)

    expect(md5.call_args.kwargs).to_equal({"usedforsecurity": False})


def test_url_raises_if_no_url():
    """test_url_raises_if_no_url
    Given
        An image URL of "" or null
    When
        I ask my library for an URL
    Then
        I get an exception that says image URL is mandatory
    """
    with expect.error_to_happen(
        ValueError, message="The image_url argument is mandatory."
    ):
        plain_image_url()


def test_url_width_height_1():
    """test_url_width_height_1
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 300
    When
        I ask my library for an URL
    Then
        I get "300x0/<image URL>" as URL
    """
    url = plain_image_url(width=300, image_url=IMAGE_URL)

    expect(url).to_equal(f"300x0/{IMAGE_URL}")


def test_url_width_height_2():
    """test_url_width_height_2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a height of 300
    When
        I ask my library for an URL
    Then
        I get "0x300/<image URL>" as URL
    """
    url = plain_image_url(height=300, image_url=IMAGE_URL)

    expect(url).to_equal(f"0x300/{IMAGE_URL}")


def test_url_width_height_3():
    """test_url_width_height_3
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
    When
        I ask my library for an URL
    Then
        I get "200x300/<image URL>" as URL
    """
    url = plain_image_url(width=200, height=300, image_url=IMAGE_URL)

    expect(url).to_equal(f"200x300/{IMAGE_URL}")


def test_url_width_height_4():
    """test_url_width_height_4
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of orig
    When
        I ask my library for an URL
    Then
        I get "origx0/<image URL>" as URL
    """
    url = plain_image_url(width="orig", image_url=IMAGE_URL)

    expect(url).to_equal(f"origx0/{IMAGE_URL}")


def test_url_width_height_5():
    """test_url_width_height_5
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a height of orig
    When
        I ask my library for an URL
    Then
        I get "0xorig/<image URL>" as URL
    """
    url = plain_image_url(height="orig", image_url=IMAGE_URL)

    expect(url).to_equal(f"0xorig/{IMAGE_URL}")


def test_url_width_height_6():
    """test_url_width_height_6
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 100
        And a height of orig
    When
        I ask my library for an URL
    Then
        I get "100xorig/<image URL>" as URL
    """
    url = plain_image_url(width=100, height="orig", image_url=IMAGE_URL)

    expect(url).to_equal(f"100xorig/{IMAGE_URL}")


def test_url_width_height_7():
    """test_url_width_height_7
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a height of 100
        And a width of orig
    When
        I ask my library for an URL
    Then
        I get "origx100/<image URL>" as URL
    """
    url = plain_image_url(width="orig", height=100, image_url=IMAGE_URL)

    expect(url).to_equal(f"origx100/{IMAGE_URL}")


def test_url_width_height_8():
    """test_url_width_height_8
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a height of orig
        And a width of orig
    When
        I ask my library for an URL
    Then
        I get "origxorig/<image URL>" as URL
    """
    url = plain_image_url(width="orig", height="orig", image_url=IMAGE_URL)

    expect(url).to_equal(f"origxorig/{IMAGE_URL}")


def test_smart_url():
    """test_smart_url
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
        And the smart flag
    When
        I ask my library for an URL
    Then
        I get "200x300/smart/<image URL>" as URL
    """
    url = plain_image_url(width=200, height=300, smart=True, image_url=IMAGE_URL)

    expect(url).to_equal(f"200x300/smart/{IMAGE_URL}")


def test_fit_in_url():
    """test_fit_in_url
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
        And the fit-in flag
    When
        I ask my library for an URL
    Then
        I get "fit-in/200x300/<image URL>" as URL
    """
    url = plain_image_url(width=200, height=300, fit_in=True, image_url=IMAGE_URL)

    expect(url).to_equal(f"fit-in/200x300/{IMAGE_URL}")


def test_adaptive_fit_in_url():
    """test_adaptive_fit_in_url
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
        And the adaptive fit-in flag
    When
        I ask my library for an URL
    Then
        I get "adaptive-fit-in/200x300/<image URL>" as URL
    """
    url = plain_image_url(
        width=200, height=300, adaptive_fit_in=True, image_url=IMAGE_URL
    )

    expect(url).to_equal(f"adaptive-fit-in/200x300/{IMAGE_URL}")


def test_fit_in_fails_if_no_width_supplied():
    with expect.error_to_happen(
        ValueError,
        message="When using fit-in or full-fit-in, "
        "you must specify width and/or height.",
    ):
        plain_image_url(fit_in=True, image_url=IMAGE_URL)


def test_full_fit_in_fails_if_no_width_supplied():
    with expect.error_to_happen(
        ValueError,
        message="When using fit-in or full-fit-in, "
        "you must specify width and/or height.",
    ):
        plain_image_url(full_fit_in=True, image_url=IMAGE_URL)


def test_adaptive_fit_in_fails_if_no_width_supplied():
    with expect.error_to_happen(
        ValueError,
        message="When using fit-in or full-fit-in, "
        "you must specify width and/or height.",
    ):
        plain_image_url(adaptive_fit_in=True, image_url=IMAGE_URL)


def test_adaptive_full_fit_in_fails_if_no_width_supplied():
    with expect.error_to_happen(
        ValueError,
        message="When using fit-in or full-fit-in, "
        "you must specify width and/or height.",
    ):
        plain_image_url(adaptive_full_fit_in=True, image_url=IMAGE_URL)


def test_full_fit_in_url():
    """test_full_fit_in_url
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
        And the full-fit-in flag
    When
        I ask my library for an URL
    Then
        I get "full-fit-in/200x300/<image URL>" as URL
    """
    url = plain_image_url(width=200, height=300, full_fit_in=True, image_url=IMAGE_URL)

    expect(url).to_equal(f"full-fit-in/200x300/{IMAGE_URL}")


def test_adaptive_full_fit_in_url():
    """test_adaptive_full_fit_in_url
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
        And the adaptive full-fit-in flag
    When
        I ask my library for an URL
    Then
        I get "adaptive-full-fit-in/200x300/<image URL>" as URL
    """
    url = plain_image_url(
        width=200, height=300, adaptive_full_fit_in=True, image_url=IMAGE_URL
    )

    expect(url).to_equal(f"adaptive-full-fit-in/200x300/{IMAGE_URL}")


def test_flip_1():
    """test_flip_1
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And the flip flag
    When
        I ask my library for an URL
    Then
        I get "-0x0/<image URL>" as URL
    """
    url = plain_image_url(flip=True, image_url=IMAGE_URL)

    expect(url).to_equal(f"-0x0/{IMAGE_URL}")


def test_flip_2():
    """test_flip_2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And the flip flag
    When
        I ask my library for an URL
    Then
        I get "-200x0/<image URL>" as URL
    """
    url = plain_image_url(flip=True, width=200, image_url=IMAGE_URL)

    expect(url).to_equal(f"-200x0/{IMAGE_URL}")


def test_flop_1():
    """test_flop_1
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And the flop flag
    When
        I ask my library for an URL
    Then
        I get "0x-0/<image URL>" as URL
    """
    url = plain_image_url(flop=True, image_url=IMAGE_URL)

    expect(url).to_equal(f"0x-0/{IMAGE_URL}")


def test_flop_2():
    """test_flop_2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a height of 200
        And the flop flag
    When
        I ask my library for an URL
    Then
        I get "0x-200/<image URL>" as URL
    """
    url = plain_image_url(flop=True, height=200, image_url=IMAGE_URL)

    expect(url).to_equal(f"0x-200/{IMAGE_URL}")


def test_flip_flop():
    """test_flip_flop
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And the flip flag
        And the flop flag
    When
        I ask my library for an URL
    Then
        I get "-0x-0/<image URL>" as URL
    """
    url = plain_image_url(flip=True, flop=True, image_url=IMAGE_URL)

    expect(url).to_equal(f"-0x-0/{IMAGE_URL}")


def test_flip_flop2():
    """test_flip_flop2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a width of 200
        And a height of 300
        And the flip flag
        And the flop flag
    When
        I ask my library for an URL
    Then
        I get "-200x-300/<image URL>" as URL
    """
    url = plain_image_url(
        flip=True, flop=True, width=200, height=300, image_url=IMAGE_URL
    )

    expect(url).to_equal(f"-200x-300/{IMAGE_URL}")


def test_horizontal_alignment():
    """test_horizontal_alignment
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'left' horizontal alignment option
    When
        I ask my library for an URL
    Then
        I get "left/<image URL>" as URL
    """
    url = plain_image_url(halign="left", image_url=IMAGE_URL)

    expect(url).to_equal(f"left/{IMAGE_URL}")


def test_horizontal_alignment2():
    """test_horizontal_alignment2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'center' horizontal alignment option
    When
        I ask my library for an URL
    Then
        I get "<image URL>" as URL
    """
    url = plain_image_url(halign="center", image_url=IMAGE_URL)

    expect(url).to_equal(IMAGE_URL)


def test_vertical_alignment():
    """test_vertical_alignment
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'top' vertical alignment option
    When
        I ask my library for an URL
    Then
        I get "top/<image URL>" as URL
    """
    url = plain_image_url(valign="top", image_url=IMAGE_URL)

    expect(url).to_equal(f"top/{IMAGE_URL}")


def test_vertical_alignment2():
    """test_vertical_alignment2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'middle' vertical alignment option
    When
        I ask my library for an URL
    Then
        I get "<image URL>" as URL
    """
    url = plain_image_url(valign="middle", image_url=IMAGE_URL)

    expect(url).to_equal(IMAGE_URL)


def test_both_alignments():
    """test_both_alignments
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'left' horizontal alignment option
        And a 'top' vertical alignment option
    When
        I ask my library for an URL
    Then
        I get "left/top/<image URL>" as URL
    """
    url = plain_image_url(halign="left", valign="top", image_url=IMAGE_URL)

    expect(url).to_equal(f"left/top/{IMAGE_URL}")


def test_proper_haligns():
    """test_proper_haligns"""
    with expect.error_to_happen(
        ValueError,
        message=(
            'Only "left", "center" and "right"'
            " are valid values for horizontal alignment."
        ),
    ):
        plain_image_url(halign="wrong", image_url=IMAGE_URL)


def test_proper_valigns():
    """test_proper_haligns"""
    with expect.error_to_happen(
        ValueError,
        message=(
            'Only "top", "middle" and "bottom"'
            " are valid values for vertical alignment."
        ),
    ):
        plain_image_url(valign="wrong", image_url=IMAGE_URL)


def test_proper_meta():
    """test_proper_meta
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'meta' flag
    When
        I ask my library for an URL
    Then
        I get "meta/<image URL>" as URL
    """
    url = plain_image_url(meta=True, image_url=IMAGE_URL)

    expect(f"meta/{IMAGE_URL}").to_equal(url)


def test_trim_standard():
    url = plain_image_url(trim=True, image_url=IMAGE_URL)
    expect(f"trim/{IMAGE_URL}").to_equal(url)


def test_trim_pixel_and_tolerance():
    url = plain_image_url(trim=("bottom-right", 15), image_url=IMAGE_URL)
    expect(f"trim:bottom-right:15/{IMAGE_URL}").to_equal(url)


def test_trim_pixel_only():
    url = plain_image_url(trim=("top-left", None), image_url=IMAGE_URL)
    expect(f"trim:top-left/{IMAGE_URL}").to_equal(url)


def test_trim_tolerance_only():
    url = plain_image_url(trim=(None, 15), image_url=IMAGE_URL)
    expect(f"trim::15/{IMAGE_URL}").to_equal(url)


def test_manual_crop_1():
    """test_manual_crop_1
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a manual crop left-top point of (10, 20)
        And a manual crop right-bottom point of (30, 40)
    When
        I ask my library for an URL
    Then
        I get "10x20:30x40/<image URL>" as URL
    """
    url = plain_image_url(crop=((10, 20), (30, 40)), image_url=IMAGE_URL)

    expect(f"10x20:30x40/{IMAGE_URL}").to_equal(url)


def test_manual_crop_2():
    """test_manual_crop_2
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a manual crop left-top point of (0, 0)
        And a manual crop right-bottom point of (0, 0)
    When
        I ask my library for an URL
    Then
        I get "<image URL>" as URL
    """
    url = plain_image_url(crop=((0, 0), (0, 0)), image_url=IMAGE_URL)

    expect(IMAGE_URL).to_equal(url)


def test_smart_after_alignments():
    """test_smart_after_alignments
    Given
        An image URL of "my.server.com/some/path/to/image.jpg"
        And a 'smart' flag
        And a 'left' horizontal alignment option
    When
        I ask my library for an URL
    Then
        I get "left/smart/<image URL>" as URL
    """
    url = plain_image_url(smart=True, halign="left", image_url=IMAGE_URL)

    expect(f"left/smart/{IMAGE_URL}").to_equal(url)


class UnsafeUrlTestCase(TestCase):
    def test_should_return_a_valid_unsafe_url_with_no_params(self):
        expect(f"unsafe/{IMAGE_URL}").to_equal(unsafe_url(image_url=IMAGE_URL))

    def test_should_return_an_unsafe_url_with_width_and_height(self):
        expect(f"unsafe/100x140/{IMAGE_URL}").to_equal(
            unsafe_url(image_url=IMAGE_URL, width=100, height=140),
        )

    def test_should_return_an_unsafe_url_with_crop_and_smart(self):
        expect(f"unsafe/100x140/smart/{IMAGE_URL}").to_equal(
            unsafe_url(image_url=IMAGE_URL, width=100, height=140, smart=True),
        )


def test_url_for_with_non_ascii_image_url():
    with pytest.warns(DeprecationWarning):
        url = url_for(image_url="example.com/日本.jpg")

    expect(url).to_equal("18f3625a70ea0a67ebc3d00a3fbb7cc9")
