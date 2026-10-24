# libthumbor - python extension to thumbor
# https://github.com/thumbor/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""libthumbor URL composer tests"""

import hashlib
import numbers
import re
from unittest import TestCase, mock

import pytest

from libthumbor.url import Url, plain_image_url, unsafe_url, url_for

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

    assert url == IMAGE_URL


def test_url_for_is_deprecated():
    with pytest.warns(DeprecationWarning, match=r"url_for\(\) is deprecated") as record:
        url_for(image_url=IMAGE_URL)

    assert record[0].filename == __file__


def test_url_for_replaces_the_image_url_with_its_md5():
    with pytest.warns(DeprecationWarning):
        url = url_for(width=300, image_url=IMAGE_URL)

    assert url == f"300x0/{IMAGE_MD5}"


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

    assert md5.call_args.kwargs == {"usedforsecurity": False}


def test_url_raises_if_no_url():
    """test_url_raises_if_no_url
    Given
        An image URL of "" or null
    When
        I ask my library for an URL
    Then
        I get an exception that says image URL is mandatory
    """
    with pytest.raises(ValueError) as excinfo:
        plain_image_url()
    assert str(excinfo.value) == "The image_url argument is mandatory."


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

    assert url == f"300x0/{IMAGE_URL}"


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

    assert url == f"0x300/{IMAGE_URL}"


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

    assert url == f"200x300/{IMAGE_URL}"


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

    assert url == f"origx0/{IMAGE_URL}"


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

    assert url == f"0xorig/{IMAGE_URL}"


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

    assert url == f"100xorig/{IMAGE_URL}"


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

    assert url == f"origx100/{IMAGE_URL}"


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

    assert url == f"origxorig/{IMAGE_URL}"


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

    assert url == f"200x300/smart/{IMAGE_URL}"


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

    assert url == f"fit-in/200x300/{IMAGE_URL}"


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

    assert url == f"adaptive-fit-in/200x300/{IMAGE_URL}"


@pytest.mark.parametrize(
    "option", ["fit_in", "full_fit_in", "adaptive_fit_in", "adaptive_full_fit_in"]
)
def test_fit_in_fails_if_no_width_supplied(option):
    with pytest.raises(ValueError) as excinfo:
        plain_image_url(image_url=IMAGE_URL, **{option: True})
    assert str(excinfo.value) == (
        "When using fit-in or full-fit-in, you must specify width and/or height."
    )


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

    assert url == f"full-fit-in/200x300/{IMAGE_URL}"


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

    assert url == f"adaptive-full-fit-in/200x300/{IMAGE_URL}"


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

    assert url == f"-0x0/{IMAGE_URL}"


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

    assert url == f"-200x0/{IMAGE_URL}"


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

    assert url == f"0x-0/{IMAGE_URL}"


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

    assert url == f"0x-200/{IMAGE_URL}"


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

    assert url == f"-0x-0/{IMAGE_URL}"


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

    assert url == f"-200x-300/{IMAGE_URL}"


def test_flip_with_only_a_height():
    url = plain_image_url(flip=True, height=200, image_url=IMAGE_URL)

    assert url == f"-0x200/{IMAGE_URL}"


def test_flop_with_only_a_width():
    url = plain_image_url(flop=True, width=300, image_url=IMAGE_URL)

    assert url == f"300x-0/{IMAGE_URL}"


def test_flip_flop_with_string_dimensions():
    url = plain_image_url(
        flip=True, flop=True, width="300", height="orig", image_url=IMAGE_URL
    )

    assert url == f"-300x-orig/{IMAGE_URL}"


def test_horizontal_and_vertical_flip_are_aliases_of_flip_and_flop():
    url = plain_image_url(
        horizontal_flip=True, vertical_flip=True, width=300, image_url=IMAGE_URL
    )

    assert url == f"-300x-0/{IMAGE_URL}"


def test_crop_sides_are_an_alias_of_crop():
    url = plain_image_url(
        crop_left="10",
        crop_top="20",
        crop_right="30",
        crop_bottom="40",
        image_url=IMAGE_URL,
    )

    assert url == f"10x20:30x40/{IMAGE_URL}"


def test_zero_crop_sides_add_no_crop():
    url = plain_image_url(
        crop_left=0, crop_top=0, crop_right=0, crop_bottom=0, image_url=IMAGE_URL
    )

    assert url == IMAGE_URL


def test_crop_sides_apply_when_crop_is_none():
    url = plain_image_url(
        crop=None,
        crop_left="10",
        crop_top="20",
        crop_right="30",
        crop_bottom="40",
        image_url=IMAGE_URL,
    )

    assert url == f"10x20:30x40/{IMAGE_URL}"


def test_explicit_crop_wins_over_crop_sides():
    url = plain_image_url(
        crop=((1, 2), (3, 4)),
        crop_left="10",
        crop_top="20",
        crop_right="30",
        crop_bottom="40",
        image_url=IMAGE_URL,
    )

    assert url == f"1x2:3x4/{IMAGE_URL}"


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

    assert url == f"left/{IMAGE_URL}"


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

    assert url == IMAGE_URL


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

    assert url == f"top/{IMAGE_URL}"


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

    assert url == IMAGE_URL


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

    assert url == f"left/top/{IMAGE_URL}"


def test_proper_haligns():
    """test_proper_haligns"""
    with pytest.raises(ValueError) as excinfo:
        plain_image_url(halign="wrong", image_url=IMAGE_URL)
    assert str(excinfo.value) == (
        'Only "left", "center" and "right" are valid values for horizontal alignment.'
    )


def test_proper_valigns():
    """test_proper_haligns"""
    with pytest.raises(ValueError) as excinfo:
        plain_image_url(valign="wrong", image_url=IMAGE_URL)
    assert str(excinfo.value) == (
        'Only "top", "middle" and "bottom" are valid values for vertical alignment.'
    )


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

    assert url == f"meta/{IMAGE_URL}"


def test_debug_comes_before_meta():
    url = plain_image_url(debug=True, meta=True, width=10, image_url=IMAGE_URL)

    assert url == f"debug/meta/10x0/{IMAGE_URL}"


def test_trim_standard():
    url = plain_image_url(trim=True, image_url=IMAGE_URL)
    assert url == f"trim/{IMAGE_URL}"


def test_trim_pixel_and_tolerance():
    url = plain_image_url(trim=("bottom-right", 15), image_url=IMAGE_URL)
    assert url == f"trim:bottom-right:15/{IMAGE_URL}"


def test_trim_pixel_only():
    url = plain_image_url(trim=("top-left", None), image_url=IMAGE_URL)
    assert url == f"trim:top-left/{IMAGE_URL}"


def test_trim_tolerance_only():
    url = plain_image_url(trim=(None, 15), image_url=IMAGE_URL)
    assert url == f"trim:15/{IMAGE_URL}"


def test_trim_as_a_string():
    url = plain_image_url(trim="bottom-right:10", image_url=IMAGE_URL)
    assert url == f"trim:bottom-right:10/{IMAGE_URL}"


def test_trim_without_position_or_tolerance():
    url = plain_image_url(trim=(None, None), image_url=IMAGE_URL)
    assert url == f"trim/{IMAGE_URL}"


def test_every_trim_form_is_read_by_thumbor():
    regex = re.compile(Url.regex(has_unsafe_or_hash=False))
    for trim in (True, "top-left", "15", ("bottom-right", 10), (None, 15)):
        url = plain_image_url(trim=trim, image_url=IMAGE_URL)
        assert regex.match(url)["trim"] == url.split("/", maxsplit=1)[0]


def test_invalid_trim():
    for trim in ("x", "trim:top-left", 5):
        with pytest.raises(ValueError):
            plain_image_url(trim=trim, image_url=IMAGE_URL)


def test_falsy_trim_is_ignored():
    for trim in ("", 0, None, False):
        assert plain_image_url(trim=trim, image_url=IMAGE_URL) == IMAGE_URL


def test_none_dimension_counts_as_zero():
    url = plain_image_url(width=None, height=200, image_url=IMAGE_URL)
    assert url == f"0x200/{IMAGE_URL}"


def test_zero_dimension_as_a_digit_string_counts_as_zero():
    assert plain_image_url(width="0", height="0", image_url=IMAGE_URL) == IMAGE_URL
    with pytest.raises(ValueError, match="you must specify width and/or height"):
        plain_image_url(fit_in=True, width="0", image_url=IMAGE_URL)


def test_dimensions_as_digit_strings_are_normalized():
    url = plain_image_url(width="007", height="20", flip=True, image_url=IMAGE_URL)
    assert url == f"-7x20/{IMAGE_URL}"


class Integer:
    def __init__(self, value):
        self.value = value

    def __int__(self):
        return self.value

    def __index__(self):
        return self.value

    def __ge__(self, other):
        return self.value >= other


numbers.Integral.register(Integer)


def test_integral_values_that_are_not_int():
    url = plain_image_url(
        width=Integer(300),
        crop=((Integer(1), 2), (3, 4)),
        image_url=IMAGE_URL,
    )
    assert url == f"1x2:3x4/300x0/{IMAGE_URL}"


def test_invalid_dimensions():
    for width in ("abc", " 300", 300.0, True):
        with pytest.raises(ValueError, match="width option must be an integer"):
            plain_image_url(width=width, image_url=IMAGE_URL)


def test_flags_accept_the_strings_the_django_view_accepts():
    url = plain_image_url(
        smart="false", flip="0", meta="yes", width=300, image_url=IMAGE_URL
    )
    assert url == f"meta/300x0/{IMAGE_URL}"


def test_invalid_flag():
    with pytest.raises(ValueError, match="smart option must be a boolean"):
        plain_image_url(smart="maybe", image_url=IMAGE_URL)


def test_filters_as_a_string():
    url = plain_image_url(filters="blur(2):grayscale()", image_url=IMAGE_URL)
    assert url == f"filters:blur(2):grayscale()/{IMAGE_URL}"


def test_crop_values_as_digit_strings():
    url = plain_image_url(crop=(("10", "20"), ("30", "40")), image_url=IMAGE_URL)
    assert url == f"10x20:30x40/{IMAGE_URL}"


def test_invalid_crop_values():
    for crop in (((-1, 0), (10, 10)), ((1.5, 0), (2, 2)), (("a", 0), (2, 2))):
        with pytest.raises(ValueError, match="crop values must be non-negative"):
            plain_image_url(crop=crop, image_url=IMAGE_URL)


def test_malformed_crop():
    for crop in (((1, 2), (3,)), "10x20:30x40", 5):
        with pytest.raises(ValueError, match="crop option must be a"):
            plain_image_url(crop=crop, image_url=IMAGE_URL)


def test_invalid_filters():
    with pytest.raises(ValueError, match="filters option must be a string"):
        plain_image_url(filters=5, image_url=IMAGE_URL)


def test_empty_image_url():
    for image_url in ("", None):
        with pytest.raises(ValueError, match="image_url argument is mandatory"):
            plain_image_url(image_url=image_url)


def test_only_one_fit_in_variant():
    with pytest.raises(ValueError, match="Only one of fit_in"):
        plain_image_url(
            fit_in=True, adaptive_fit_in=True, width=300, image_url=IMAGE_URL
        )


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

    assert url == f"10x20:30x40/{IMAGE_URL}"


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

    assert url == IMAGE_URL


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

    assert url == f"left/smart/{IMAGE_URL}"


class UnsafeUrlTestCase(TestCase):
    def test_should_return_a_valid_unsafe_url_with_no_params(self):
        assert unsafe_url(image_url=IMAGE_URL) == f"unsafe/{IMAGE_URL}"

    def test_should_return_an_unsafe_url_with_width_and_height(self):
        assert (
            unsafe_url(image_url=IMAGE_URL, width=100, height=140)
            == f"unsafe/100x140/{IMAGE_URL}"
        )

    def test_should_return_an_unsafe_url_with_crop_and_smart(self):
        assert (
            unsafe_url(image_url=IMAGE_URL, width=100, height=140, smart=True)
            == f"unsafe/100x140/smart/{IMAGE_URL}"
        )


def test_url_for_with_non_ascii_image_url():
    with pytest.warns(DeprecationWarning):
        url = url_for(image_url="example.com/日本.jpg")

    assert url == "18f3625a70ea0a67ebc3d00a3fbb7cc9"
