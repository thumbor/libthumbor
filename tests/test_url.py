# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

# pylint: disable=line-too-long

import re
from unittest import TestCase

import pytest

from libthumbor.url import Url, plain_image_url


class UrlTestCase(TestCase):
    def setUp(self):
        Url.compiled_regex = None

    def test_can_get_regex(self):
        regex = Url.regex()

        assert regex == (
            "/?(?:(?:(?P<unsafe>unsafe)|(?P<hash>.+?))/)?(?:(?P<debug>debug)/)?(?:(?P<meta>meta)/)?"
            "(?:(?P<trim>trim(?::(?:top-left|bottom-right))?(?::\\d+)?)/)?"
            "(?:(?P<crop_left>\\d+)x(?P<crop_top>\\d+):(?P<crop_right>\\d+)x(?P<crop_bottom>\\d+)/)?"
            "(?:(?P<adaptive>adaptive-)?(?P<full>full-)?(?P<fit_in>fit-in)/)?(?:(?P<horizontal_flip>-)?"
            "(?P<width>(?:\\d+|orig))?x(?P<vertical_flip>-)?(?P<height>(?:\\d+|orig))?/)?"
            "(?:(?P<halign>left|right|center)/)?(?:(?P<valign>top|bottom|middle)/)?"
            "(?:(?P<smart>smart)/)?(?:filters:(?P<filters>.+?\\))/)?(?P<image>.+)"
        )

    def test_can_get_regex_without_unsafe(self):
        regex = Url.regex(False)

        assert regex == (
            "/?(?:(?P<debug>debug)/)?(?:(?P<meta>meta)/)?"
            "(?:(?P<trim>trim(?::(?:top-left|bottom-right))?(?::\\d+)?)/)?"
            "(?:(?P<crop_left>\\d+)x(?P<crop_top>\\d+):(?P<crop_right>\\d+)x(?P<crop_bottom>\\d+)/)?"
            "(?:(?P<adaptive>adaptive-)?(?P<full>full-)?(?P<fit_in>fit-in)/)?(?:(?P<horizontal_flip>-)?"
            "(?P<width>(?:\\d+|orig))?x(?P<vertical_flip>-)?(?P<height>(?:\\d+|orig))?/)?"
            "(?:(?P<halign>left|right|center)/)?(?:(?P<valign>top|bottom|middle)/)?"
            "(?:(?P<smart>smart)/)?(?:filters:(?P<filters>.+?\\))/)?(?P<image>.+)"
        )

    def test_parsing_invalid_url(self):
        assert Url.compiled_regex is None

        url = ""
        assert Url.parse_decrypted(url) is None

    def test_parsing_complete_url(self):
        url = (
            "/debug/meta/trim/300x200:400x500/adaptive-full-fit-in/-300x-400/"
            "left/top/smart/filters:brightness(100)/some/image.jpg"
        )

        expected = {
            "trim": "trim",
            "full": True,
            "halign": "left",
            "fit_in": True,
            "vertical_flip": True,
            "image": "some/image.jpg",
            "crop": {"top": 200, "right": 400, "bottom": 500, "left": 300},
            "height": 400,
            "width": 300,
            "meta": True,
            "horizontal_flip": True,
            "filters": "brightness(100)",
            "valign": "top",
            "debug": True,
            "adaptive": True,
            "smart": True,
        }

        result = Url.parse_decrypted(url)
        assert result is not None
        assert result == expected

        # do it again to use compiled regex
        result = Url.parse_decrypted(url)
        assert result is not None
        assert result == expected

    def test_can_generate_url(self):
        url = Url.generate_options(
            debug=True,
            width=300,
            height=200,
            smart=True,
            meta=True,
            trim=True,
            adaptive=True,
            full=True,
            fit_in=True,
            horizontal_flip=True,
            vertical_flip=True,
            halign="left",
            valign="top",
            crop_left=100,
            crop_top=100,
            crop_right=400,
            crop_bottom=400,
            filters="brightness(100)",
        )

        assert url == (
            "debug/meta/trim/100x100:400x400/adaptive-full-fit-in/-300x-200/left/top/smart/filters:brightness(100)"
        )

    def test_can_generate_url_with_defaults(self):
        url = Url.generate_options()

        assert url == ""

    def test_can_generate_url_with_fitin(self):
        url = Url.generate_options(fit_in=True, adaptive=False, full=False)

        assert url == "fit-in"

    def test_can_generate_url_with_custom_trim(self):
        url = Url.generate_options(
            debug=True,
            width=300,
            height=200,
            smart=True,
            meta=True,
            trim="bottom-right:10",
            adaptive=True,
            full=True,
            fit_in=True,
            horizontal_flip=True,
            vertical_flip=True,
            halign="left",
            valign="top",
            crop_left=100,
            crop_top=100,
            crop_right=400,
            crop_bottom=400,
            filters="brightness(100)",
        )

        assert url == (
            "debug/meta/trim:bottom-right:10/100x100:400x400/adaptive-full-fit-in/-300x-200/left/top/smart/filters:brightness(100)"
        )

    def test_generate_options_trim_matches_the_cryptourl_forms(self):
        regex = re.compile(Url.regex(has_unsafe_or_hash=False))
        for trim, expected in (
            (("top-left", 10), "trim:top-left:10"),
            ((None, 15), "trim:15"),
            ("bottom-right", "trim:bottom-right"),
        ):
            url = Url.generate_options(trim=trim)
            assert url == expected
            assert regex.match(f"{url}/a.jpg")["trim"] == expected

    def test_generate_options_rejects_a_trim_thumbor_cannot_read(self):
        with pytest.raises(ValueError):
            Url.generate_options(trim="300x200")

    def test_generate_options_accepts_a_filters_sequence(self):
        url = Url.generate_options(filters=["blur(2)", "grayscale()"])

        assert url == "filters:blur(2):grayscale()"

    def test_generate_options_partial_crop_counts_missing_sides_as_zero(self):
        assert Url.generate_options(crop_right=10) == "0x0:10x0"

    def test_generate_options_rejects_a_negative_crop(self):
        with pytest.raises(ValueError, match="crop values must be non-negative"):
            Url.generate_options(crop_left=-1)

    def test_generate_options_validates_alignments(self):
        with pytest.raises(ValueError, match="horizontal alignment"):
            Url.generate_options(halign="bogus")
        with pytest.raises(ValueError, match="vertical alignment"):
            Url.generate_options(valign="bogus")

    def test_generate_options_adaptive_and_full_require_fit_in(self):
        for option in ("adaptive", "full"):
            with pytest.raises(ValueError, match="require fit_in"):
                Url.generate_options(width=10, **{option: True})

    def test_parse_decrypted_without_options(self):
        parsed = Url.parse_decrypted("images.example.com/a.jpg")

        assert parsed["trim"] is None
        assert parsed["crop"] == {"left": 0, "top": 0, "right": 0, "bottom": 0}
        assert parsed["image"] == "images.example.com/a.jpg"

    def test_composer_parser_and_generate_options_agree(self):
        for options in (
            {},
            {"debug": True, "meta": True, "trim": True, "smart": True},
            {"trim": ("top-left", 10), "crop": ((10, 20), (30, 40))},
            {"adaptive_full_fit_in": True, "width": 300, "flip": True},
            {"width": "orig", "height": 200, "flop": True, "halign": "left"},
            {"valign": "bottom", "filters": ["blur(2)", "grayscale()"]},
        ):
            path = plain_image_url(image_url="a.jpg", **options)
            parsed = Url.parse_decrypted(path)
            trim = parsed["trim"]
            regenerated = Url.generate_options(
                debug=parsed["debug"],
                meta=parsed["meta"],
                trim=None if trim is None else trim.partition(":")[2] or True,
                crop_left=parsed["crop"]["left"],
                crop_top=parsed["crop"]["top"],
                crop_right=parsed["crop"]["right"],
                crop_bottom=parsed["crop"]["bottom"],
                fit_in=parsed["fit_in"],
                adaptive=parsed["adaptive"],
                full=parsed["full"],
                width=parsed["width"],
                height=parsed["height"],
                horizontal_flip=parsed["horizontal_flip"],
                vertical_flip=parsed["vertical_flip"],
                halign=parsed["halign"],
                valign=parsed["valign"],
                smart=parsed["smart"],
                filters=parsed["filters"],
            )

            assert parsed["image"] == "a.jpg"
            assert "/".join(filter(None, (regenerated, "a.jpg"))) == path

    def test_parse_decrypted_with_more_digits_than_int_accepts(self):
        too_long = "9" * 5000

        assert Url.parse_decrypted(f"{too_long}x10/image.jpg") is None
        assert Url.parse_decrypted(f"1x1:{too_long}x1/image.jpg") is None
