#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""libthumbor cryptography tests"""

from unittest import TestCase

from preggy import expect

from libthumbor.crypto import CryptoURL

IMAGE_URL = "my.server.com/some/path/to/image.jpg"
KEY = b"my-security-key"


class NewFormatUrlTestsMixin:
    def test_generated_url_1(self):
        url = self.crypto.generate(image_url=IMAGE_URL, width=300, height=200)
        expect(url).to_equal(
            "/8ammJH8D-7tXy6kU3lTvoXlhu4o=/300x200/my.server.com/some/path/to/image.jpg"
        )

    def test_generated_url_2(self):
        url = self.crypto.generate(
            image_url=IMAGE_URL, width=300, height=200, crop=((10, 10), (200, 200))
        )
        expect(url).to_equal(
            "/B35oBEIwztbc3jm7vsdqLez2C78=/10x10:200x200/300x200/"
            "my.server.com/some/path/to/image.jpg"
        )

    def test_generated_url_3(self):
        url = self.crypto.generate(
            image_url=IMAGE_URL,
            width=300,
            height=200,
            crop=((10, 10), (200, 200)),
            filters=("brightness(20)", "contrast(10)"),
        )
        expect(url).to_equal(
            "/as8U2DbUUtTMgvPF26LkjS3MocY=/10x10:200x200/300x200/"
            "filters:brightness(20):contrast(10)/my.server.com/some/path/to/image.jpg"
        )

    def test_generated_url_4(self):
        url = self.crypto.generate(
            image_url=IMAGE_URL,
            width=300,
            height=200,
            crop=((10, 10), (200, 200)),
            filters=("brightness(20)", "contrast(10)"),
        )
        expect(url).to_equal(
            "/as8U2DbUUtTMgvPF26LkjS3MocY=/10x10:200x200/300x200/"
            "filters:brightness(20):contrast(10)/my.server.com/some/path/to/image.jpg"
        )
        # making sure no internal state affects subsequent calls.
        url = self.crypto.generate(
            image_url=IMAGE_URL,
            width=300,
            height=200,
            crop=((10, 10), (200, 200)),
            filters=("brightness(20)", "contrast(10)"),
        )
        expect(url).to_equal(
            "/as8U2DbUUtTMgvPF26LkjS3MocY=/10x10:200x200/300x200/"
            "filters:brightness(20):contrast(10)/my.server.com/some/path/to/image.jpg"
        )


class NewFormatUrl(TestCase, NewFormatUrlTestsMixin):
    def setUp(self):
        self.crypto = CryptoURL(KEY)


class NewFormatUrlWithUnicodeKey(TestCase, NewFormatUrlTestsMixin):
    def setUp(self):
        self.crypto = CryptoURL(KEY)


class GenerateWithUnsafeTestCase(TestCase):
    def setUp(self):
        self.crypto = CryptoURL(KEY)

    def test_should_pass_unsafe_to_generate_and_get_an_unsafe_url(self):
        url = self.crypto.generate(
            image_url=IMAGE_URL, crop=((10, 20), (30, 40)), unsafe=True
        )
        expect(url.startswith("unsafe")).to_be_true()

    def test_should_not_get_an_unsafe_url_when_unsafe_is_false(self):
        url = self.crypto.generate(
            image_url=IMAGE_URL, crop=((10, 20), (30, 40)), unsafe=False
        )
        expect(url.startswith("unsafe")).to_be_false()


class KeyWithSpecialCharactersTestCase(TestCase):
    def setUp(self):
        self.crypto = CryptoURL("cafécompãodequeijo")

    def test_should_generate_url_with_key_with_special_characters(self):
        url = self.crypto.generate(image_url=IMAGE_URL)
        expect(url).to_equal(
            "/MrRd4GRirTQ0JO3vM2slr4rT5Fk=/my.server.com/some/path/to/image.jpg"
        )
