# libthumbor - python extension to thumbor
# https://github.com/thumbor/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""libthumbor generic views tests"""

import os

import pytest
from preggy import expect

from libthumbor.crypto import CryptoURL

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.testproj.testproj.settings"

try:
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured
    from django.http import QueryDict
    from django.test import TestCase, override_settings

    DJANGO_PRESENT = True
except ImportError:
    DJANGO_PRESENT = False


HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_OK = 200
HTTP_BAD_REQUEST = 400


@pytest.mark.skip_if(not DJANGO_PRESENT, "django must be present to run this test")
class GenericViewsTestCase(TestCase):
    def setUp(self):
        self.url_query = QueryDict("", mutable=True)

    def test_without_url_param(self):
        for query in ("", "?image_url=", "?image_url=%20%20"):
            response = self.client.get("/gen_url/" + query)

            expect(response.status_code).to_equal(HTTP_BAD_REQUEST)
            expect(response.content.decode("utf-8")).to_equal(
                "Invalid thumbor URL parameters."
            )

    def test_generate_url_with_params_via_post(self):
        image_args = {"image_url": "globo.com/media/img/my_image.jpg"}

        response = self.client.post("/gen_url/", image_args)

        expect(response.status_code).to_equal(HTTP_METHOD_NOT_ALLOWED)
        expect(response["Content-Type"]).to_equal("text/plain")

    def test_generate_url_with_params_via_get(self):
        crypto = CryptoURL(settings.THUMBOR_SECURITY_KEY)
        image_args = {"image_url": "globo.com/media/img/my_image.jpg"}
        self.url_query.update(image_args)

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_OK)
        expect(response.content).to_equal(
            settings.THUMBOR_SERVER + crypto.generate(**image_args).strip("/")
        )

    def test_passing_invalid_value_for_width(self):
        self.url_query.update(
            {"image_url": "globo.com/media/img/my_image.jpg", "width": 1.2}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_BAD_REQUEST)
        expect(response["Content-Type"]).to_equal("text/plain")
        expect(response.content.decode("utf-8")).to_equal(
            "The width value is not an integer."
        )

    def test_passing_invalid_value_for_height(self):
        self.url_query.update(
            {"image_url": "globo.com/media/img/my_image.jpg", "height": "s"}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_BAD_REQUEST)
        expect(response.content.decode("utf-8")).to_equal(
            "The height value is not an integer."
        )

    def test_passing_invalid_aligns(self):
        self.url_query.update(
            {"image_url": "globo.com/media/img/my_image.jpg", "halign": "sss"}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_BAD_REQUEST)
        expect(response.content.decode("utf-8")).to_equal(
            "Invalid thumbor URL parameters."
        )

    def test_passing_only_one_crop_value(self):
        self.url_query.update(
            {"image_url": "globo.com/media/img/my_image.jpg", "crop_left": 100}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_BAD_REQUEST)
        expect(str(response.content)).to_include("Missing values for cropping")

    def test_passing_only_one_crop_with_invalid_value(self):
        self.url_query.update(
            {
                "image_url": "globo.com/media/img/my_image.jpg",
                "crop_top": "bla",
                "crop_left": 200,
                "crop_right": "1",
                "crop_bottom": "blas",
            }
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_BAD_REQUEST)
        expect(str(response.content)).to_include("Invalid values for cropping")

    def test_passing_various_erroneous_values(self):
        self.url_query.update(
            {
                "image_url": "globo.com/media/img/my_image.jpg",
                "crop_left": 100,
                "width": "aaa",
                "height": 123,
            }
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_BAD_REQUEST)

    def test_passing_all_params(self):
        image_args = {
            "image_url": "globo.com/media/img/my_image.jpg",
            "halign": "left",
            "valign": "middle",
            "meta": True,
            "smart": True,
            "width": 400,
            "height": 400,
            "flip": True,
            "flop": True,
        }
        self.url_query.update(image_args)
        self.url_query.update(
            {"crop_top": 100, "crop_left": 100, "crop_bottom": 200, "crop_right": 200}
        )
        image_args.update({"crop": ((100, 100), (200, 200))})

        crypto = CryptoURL(settings.THUMBOR_SECURITY_KEY)

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_OK)
        expect(response.content).to_equal(
            settings.THUMBOR_SERVER + crypto.generate(**image_args).strip("/")
        )

    def test_error_response_does_not_echo_the_parameter_value(self):
        self.url_query.update(
            {
                "image_url": "globo.com/media/img/my_image.jpg",
                "width": "<script>alert(1)</script>",
            }
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_BAD_REQUEST)
        expect(response["Content-Type"]).to_equal("text/plain")
        expect(response.content.decode("utf-8")).not_to_include("<script>")

    def test_unsafe_parameter_is_ignored(self):
        crypto = CryptoURL(settings.THUMBOR_SECURITY_KEY)
        image_args = {"image_url": "globo.com/media/img/my_image.jpg"}
        self.url_query.update(image_args)
        self.url_query.update({"unsafe": "1"})

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_OK)
        expect(response.content.decode("utf-8")).not_to_include("unsafe")
        expect(response.content).to_equal(
            settings.THUMBOR_SERVER + crypto.generate(**image_args).strip("/")
        )

    def test_false_flag_values_are_not_truthy(self):
        self.url_query.update(
            {
                "image_url": "globo.com/media/img/my_image.jpg",
                "smart": "false",
                "meta": "0",
                "flip": "off",
            }
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_OK)
        body = response.content.decode("utf-8")
        expect(body).not_to_include("/smart/")
        expect(body).not_to_include("/meta/")
        expect(body).not_to_include("-0x")

    def test_invalid_flag_value(self):
        self.url_query.update(
            {"image_url": "globo.com/media/img/my_image.jpg", "trim": "x"}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_BAD_REQUEST)
        expect(response.content.decode("utf-8")).to_equal(
            "The trim value is not a boolean."
        )

    def test_filters_are_split_on_colon(self):
        crypto = CryptoURL(settings.THUMBOR_SECURITY_KEY)
        image_args = {
            "image_url": "globo.com/media/img/my_image.jpg",
            "filters": ["blur(2)", "grayscale()"],
        }
        self.url_query.update(
            {"image_url": image_args["image_url"], "filters": "blur(2):grayscale()"}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_OK)
        expect(response.content).to_equal(
            settings.THUMBOR_SERVER + crypto.generate(**image_args).strip("/")
        )

    def test_negative_crop_values(self):
        self.url_query.update(
            {
                "image_url": "globo.com/media/img/my_image.jpg",
                "crop_left": -1,
                "crop_top": 0,
                "crop_right": 10,
                "crop_bottom": 10,
            }
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_BAD_REQUEST)
        expect(response.content.decode("utf-8")).to_include(
            "Expected non-negative integers"
        )

    def test_missing_security_key(self):
        with override_settings(THUMBOR_SECURITY_KEY=""):
            with pytest.raises(ImproperlyConfigured):
                self.client.get("/gen_url/?image_url=globo.com/media/img/my_image.jpg")

    def test_thumbor_server_is_read_at_request_time(self):
        with override_settings(THUMBOR_SERVER="https://img.example.com/"):
            response = self.client.get(
                "/gen_url/?image_url=globo.com/media/img/my_image.jpg"
            )

        expect(response.status_code).to_equal(HTTP_OK)
        expect(response.content.decode("utf-8")).to_include("https://img.example.com/")

    def test_thumbor_server_without_a_trailing_slash(self):
        crypto = CryptoURL(settings.THUMBOR_SECURITY_KEY)
        image_args = {"image_url": "globo.com/media/img/my_image.jpg"}

        with override_settings(THUMBOR_SERVER="https://img.example.com"):
            response = self.client.get("/gen_url/?image_url=" + image_args["image_url"])

        expect(response.status_code).to_equal(HTTP_OK)
        expect(response.content.decode("utf-8")).to_equal(
            "https://img.example.com/" + crypto.generate(**image_args).strip("/")
        )
