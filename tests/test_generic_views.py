#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

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
    from django.test import TestCase
    from django.http import QueryDict

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
        response = self.client.get("/gen_url/")
        expect(response.status_code).to_equal(HTTP_BAD_REQUEST)

    def test_generate_url_with_params_via_post(self):
        image_args = {"image_url": "globo.com/media/img/my_image.jpg"}

        response = self.client.post("/gen_url/", image_args)

        expect(response.status_code).to_equal(HTTP_METHOD_NOT_ALLOWED)

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
        expect(str(response.content)).to_include(
            "The width value '1.2' is not an integer."
        )

    def test_passing_invalid_value_for_height(self):
        self.url_query.update(
            {"image_url": "globo.com/media/img/my_image.jpg", "height": "s"}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_BAD_REQUEST)
        expect(str(response.content)).to_include(
            "The height value 's' is not an integer."
        )

    def test_passing_invalid_aligns(self):
        self.url_query.update(
            {"image_url": "globo.com/media/img/my_image.jpg", "halign": "sss"}
        )

        response = self.client.get("/gen_url/?" + self.url_query.urlencode())

        expect(response.status_code).to_equal(HTTP_BAD_REQUEST)

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
