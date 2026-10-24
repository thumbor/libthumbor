# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from unittest import TestCase

import pytest

from libthumbor.url_signers import BaseUrlSigner


class BaseSignerTestCase(TestCase):
    def test_can_create_signer(self):
        signer = BaseUrlSigner(security_key="something")
        assert isinstance(signer, BaseUrlSigner)
        assert signer.security_key == b"something"

    def test_can_create_signer_with_binary_key(self):
        signer = BaseUrlSigner(security_key=b"something")
        assert isinstance(signer, BaseUrlSigner)
        assert signer.security_key == b"something"

    def test_can_create_unicode_signer(self):
        signer = BaseUrlSigner(security_key="téste")
        assert isinstance(signer, BaseUrlSigner)
        assert signer.security_key == "téste".encode("utf-8")

    def test_rejects_key_that_is_not_str_or_bytes(self):
        with pytest.raises(TypeError, match="NoneType"):
            BaseUrlSigner(security_key=None)

    def test_can_validate_url(self):
        class TestSigner(BaseUrlSigner):
            def signature(self, url):
                return f"{url}+1"

        signer = TestSigner(security_key="téste")
        assert signer.validate("http://www.test.com+1", "http://www.test.com")

    def test_has_abstract_method(self):
        signer = BaseUrlSigner(security_key="téste")

        with pytest.raises(NotImplementedError):
            signer.signature("test-url")
