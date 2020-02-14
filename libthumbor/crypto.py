#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""Encrypted URLs for thumbor encryption."""

from __future__ import absolute_import

import base64
import hashlib
import hmac

from six import PY3, b, text_type

from libthumbor.url import plain_image_url, unsafe_url


class CryptoURL:
    """Class responsible for generating encrypted URLs for thumbor"""

    def __init__(self, key):
        """
        Initializes the encryptor with the proper key
        :param key: secret key to use for hashing.
        """

        if isinstance(key, text_type):
            key = str(key)
        self.key = key
        self.hmac = hmac.new(b(key), digestmod=hashlib.sha1)

    def generate_new(self, options):
        url = plain_image_url(**options)
        _hmac = self.hmac.copy()
        _hmac.update(text_type(url).encode("utf-8"))
        signature = base64.urlsafe_b64encode(_hmac.digest())

        if PY3:
            signature = signature.decode("ascii")
        return "/%s/%s" % (signature, url)

    def generate(self, **options):
        """Generates an encrypted URL with the specified options"""

        if options.get("unsafe", False):
            return unsafe_url(**options)

        return self.generate_new(options)
