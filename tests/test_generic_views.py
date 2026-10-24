# libthumbor - python extension to thumbor
# https://github.com/thumbor/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""libthumbor generic views tests"""

import os

import pytest

from libthumbor.crypto import CryptoURL

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.testproj.testproj.settings"

try:
    import django
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured
    from django.http import QueryDict
    from django.test import RequestFactory, TestCase, override_settings
    from django.urls import resolve
except ImportError:
    DJANGO_PRESENT = False
else:
    django.setup()
    DJANGO_PRESENT = True


HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403
VALIDATOR = "tests.testproj.testproj.thumbor.validate_thumbor_url"


def body(response):
    return response.content.decode()


@pytest.mark.skip_if(not DJANGO_PRESENT, "django must be present to run this test")
class GenericViewsTestCase(TestCase):
    def setUp(self):
        self.url_query = QueryDict("", mutable=True)

    def test_without_url_param(self):
        for query in ("", "?image_url=", "?image_url=%20%20"):
            response = self.client.get("/gen_url/" + query)

            assert response.status_code == HTTP_BAD_REQUEST
            assert body(response) == "Invalid thumbor URL parameters."

    def test_generate_url_with_params_via_post(self):
        image_args = {"image_url": "globo.com/media/img/my_image.jpg"}

        response = self.client.post("/gen_url/", image_args)

        assert response.status_code == HTTP_METHOD_NOT_ALLOWED
        assert response["Content-Type"] == "text/plain"

    def test_generate_url_with_params_via_get(self):
        crypto = CryptoURL(settings.THUMBOR_SECURITY_KEY)
        image_args = {"image_url": "globo.com/media/img/my_image.jpg"}
        self.url_query.update(image_args)

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        assert response.status_code == HTTP_OK
        assert body(response) == (
            settings.THUMBOR_SERVER + crypto.generate(**image_args).strip("/")
        )

    def test_passing_invalid_value_for_width(self):
        self.url_query.update(
            {"image_url": "globo.com/media/img/my_image.jpg", "width": 1.2}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        assert response.status_code == HTTP_BAD_REQUEST
        assert response["Content-Type"] == "text/plain"
        assert body(response) == "The width value is not an integer."

    def test_passing_invalid_value_for_height(self):
        self.url_query.update(
            {"image_url": "globo.com/media/img/my_image.jpg", "height": "s"}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        assert response.status_code == HTTP_BAD_REQUEST
        assert body(response) == "The height value is not an integer."

    def test_passing_invalid_aligns(self):
        self.url_query.update(
            {"image_url": "globo.com/media/img/my_image.jpg", "halign": "sss"}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        assert response.status_code == HTTP_BAD_REQUEST
        assert body(response) == "Invalid thumbor URL parameters."

    def test_passing_only_one_crop_value(self):
        self.url_query.update(
            {"image_url": "globo.com/media/img/my_image.jpg", "crop_left": 100}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        assert response.status_code == HTTP_BAD_REQUEST
        assert "Missing values for cropping" in body(response)

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

        assert response.status_code == HTTP_BAD_REQUEST
        assert "Invalid values for cropping" in body(response)

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

        assert response.status_code == HTTP_BAD_REQUEST

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

        assert response.status_code == HTTP_OK
        assert body(response) == (
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

        assert response.status_code == HTTP_BAD_REQUEST
        assert response["Content-Type"] == "text/plain"
        assert "<script>" not in body(response)

    def test_unsafe_parameter_is_ignored(self):
        crypto = CryptoURL(settings.THUMBOR_SECURITY_KEY)
        image_args = {"image_url": "globo.com/media/img/my_image.jpg"}
        self.url_query.update(image_args)
        self.url_query.update({"unsafe": "1"})

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        assert response.status_code == HTTP_OK
        assert "unsafe" not in body(response)
        assert body(response) == (
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

        assert response.status_code == HTTP_OK
        url = body(response)
        assert "/smart/" not in url
        assert "/meta/" not in url
        assert "-0x" not in url

    def test_invalid_flag_value(self):
        self.url_query.update(
            {"image_url": "globo.com/media/img/my_image.jpg", "trim": "x"}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        assert response.status_code == HTTP_BAD_REQUEST
        assert body(response) == "The trim value is not a boolean."

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

        assert response.status_code == HTTP_OK
        assert body(response) == (
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

        assert response.status_code == HTTP_BAD_REQUEST
        assert "Expected non-negative integers" in body(response)

    def test_missing_security_key(self):
        with override_settings(THUMBOR_SECURITY_KEY=""):
            with pytest.raises(ImproperlyConfigured):
                self.client.get("/gen_url/?image_url=globo.com/media/img/my_image.jpg")

    def test_thumbor_server_is_read_at_request_time(self):
        with override_settings(THUMBOR_SERVER="https://img.example.com/"):
            response = self.client.get(
                "/gen_url/?image_url=globo.com/media/img/my_image.jpg"
            )

        assert response.status_code == HTTP_OK
        assert body(response).startswith("https://img.example.com/")

    def test_thumbor_server_without_a_trailing_slash(self):
        crypto = CryptoURL(settings.THUMBOR_SECURITY_KEY)
        image_args = {"image_url": "globo.com/media/img/my_image.jpg"}

        with override_settings(THUMBOR_SERVER="https://img.example.com"):
            response = self.client.get("/gen_url/?image_url=" + image_args["image_url"])

        assert response.status_code == HTTP_OK
        assert body(response) == (
            "https://img.example.com/" + crypto.generate(**image_args).strip("/")
        )


@override_settings(THUMBOR_URL_VALIDATOR=VALIDATOR)
class UrlValidatorTestCase(TestCase):
    def signed_in_get(self, query):
        request = RequestFactory().get("/gen_url/", query)
        request.user = type("User", (), {"is_authenticated": True})()
        return resolve("/gen_url/").func(request)

    def test_rejects_with_forbidden_when_the_validator_denies(self):
        response = self.client.get("/gen_url/?image_url=images.example.com/a.jpg")

        assert response.status_code == HTTP_FORBIDDEN

    def test_rejects_with_bad_request_and_the_validator_message(self):
        response = self.signed_in_get({"image_url": "evil.example.com/a.jpg"})

        assert response.status_code == HTTP_BAD_REQUEST
        assert response["Content-Type"] == "text/plain"
        assert body(response) == "Images must come from images.example.com."

    def test_validator_compares_the_host_not_a_prefix(self):
        for image_url in (
            "images.example.com.evil.com/a.jpg",
            "evil.com/images.example.com/a.jpg",
            "images.example.com@evil.com/a.jpg",
            "http://evil.com/?images.example.com/a.jpg",
        ):
            response = self.signed_in_get({"image_url": image_url})

            assert response.status_code == HTTP_BAD_REQUEST, image_url

        response = self.signed_in_get({"image_url": "http://images.example.com/a.jpg"})
        assert response.status_code == HTTP_OK

    def test_validator_sees_the_parsed_options(self):
        response = self.signed_in_get(
            {"image_url": "images.example.com/a.jpg", "filters": "blur(2)"}
        )

        assert response.status_code == HTTP_BAD_REQUEST
        assert body(response) == "Filters are not allowed."

    def test_accepted_requests_are_signed(self):
        crypto = CryptoURL(settings.THUMBOR_SECURITY_KEY)
        image_args = {"image_url": "images.example.com/a.jpg", "width": 300}

        response = self.signed_in_get(image_args)

        assert response.status_code == HTTP_OK
        assert body(response) == (
            settings.THUMBOR_SERVER + crypto.generate(**image_args).strip("/")
        )

    def test_validator_can_be_a_callable(self):
        calls = []

        with override_settings(
            THUMBOR_URL_VALIDATOR=lambda request, options: calls.append(options)
        ):
            response = self.client.get("/gen_url/?image_url=a.jpg&width=300")

        assert response.status_code == HTTP_OK
        assert calls == [{"image_url": "a.jpg", "width": 300}]

    def test_unimportable_validator(self):
        with override_settings(THUMBOR_URL_VALIDATOR="tests.missing.validate"):
            with pytest.raises(ImproperlyConfigured):
                self.client.get("/gen_url/?image_url=a.jpg")
