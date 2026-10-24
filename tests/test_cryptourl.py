# libthumbor - python extension to thumbor
# https://github.com/thumbor/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""libthumbor cryptography tests"""

from unittest import TestCase

from libthumbor import Signer
from libthumbor.crypto import CryptoURL

IMAGE_URL = "my.server.com/some/path/to/image.jpg"
KEY = b"my-security-key"


class NewFormatUrlTestsMixin:
    def test_generated_url_1(self):
        url = self.crypto.generate(image_url=IMAGE_URL, width=300, height=200)
        assert url == (
            "/8ammJH8D-7tXy6kU3lTvoXlhu4o=/300x200/my.server.com/some/path/to/image.jpg"
        )

    def test_generated_url_2(self):
        url = self.crypto.generate(
            image_url=IMAGE_URL, width=300, height=200, crop=((10, 10), (200, 200))
        )
        assert url == (
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
        assert url == (
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
        assert url == (
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
        assert url == (
            "/as8U2DbUUtTMgvPF26LkjS3MocY=/10x10:200x200/300x200/"
            "filters:brightness(20):contrast(10)/my.server.com/some/path/to/image.jpg"
        )


class NewFormatUrl(TestCase, NewFormatUrlTestsMixin):
    def setUp(self):
        self.crypto = CryptoURL(KEY)


class NewFormatUrlWithUnicodeKey(TestCase, NewFormatUrlTestsMixin):
    def setUp(self):
        self.crypto = CryptoURL(KEY.decode("utf-8"))


class GenerateWithUnsafeTestCase(TestCase):
    def setUp(self):
        self.crypto = CryptoURL(KEY)

    def test_should_pass_unsafe_to_generate_and_get_an_unsafe_url(self):
        url = self.crypto.generate(
            image_url=IMAGE_URL, crop=((10, 20), (30, 40)), unsafe=True
        )
        assert url.startswith("unsafe")

    def test_should_not_get_an_unsafe_url_when_unsafe_is_false(self):
        url = self.crypto.generate(
            image_url=IMAGE_URL, crop=((10, 20), (30, 40)), unsafe=False
        )
        assert not url.startswith("unsafe")


class NonAsciiKeyTests(TestCase):
    def test_signature_matches_the_signer_used_by_thumbor(self):
        key = "chave-ação-日本"
        url = "300x200/" + IMAGE_URL
        generated = CryptoURL(key).generate(image_url=IMAGE_URL, width=300, height=200)
        expected = Signer(key).signature(url).decode("ascii")
        assert generated == f"/{expected}/{url}"

    def test_non_ascii_image_url(self):
        key = "my-security-key"
        url = "example.com/日本.jpg"
        generated = CryptoURL(key).generate(image_url=url)
        expected = Signer(key).signature(url).decode("ascii")
        assert generated == f"/{expected}/{url}"
