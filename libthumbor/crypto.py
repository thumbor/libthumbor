# libthumbor - python extension to thumbor
# https://github.com/thumbor/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""Encrypted URLs for thumbor encryption."""

import base64
import hashlib
import hmac
import warnings

from libthumbor.url import KNOWN_OPTIONS, plain_image_url, unsafe_url


class CryptoURL:
    """Class responsible for generating encrypted URLs for thumbor"""

    def __init__(self, key):
        """
        Initializes the encryptor with the proper key
        :param key: secret key to use for hashing.
        """

        if isinstance(key, str):
            key = key.encode("utf-8")
        self.key = key
        self.hmac = hmac.new(self.key, digestmod=hashlib.sha1)

    def generate_new(self, options):
        url = plain_image_url(**options)
        _hmac = self.hmac.copy()
        _hmac.update(url.encode("utf-8"))
        signature = base64.urlsafe_b64encode(_hmac.digest()).decode("ascii")

        return f"/{signature}/{url}"

    def generate(self, **options):
        """Generates an encrypted URL with the specified options"""

        unknown = sorted(options.keys() - KNOWN_OPTIONS)
        if unknown:
            warnings.warn(
                f"Ignoring unknown thumbor URL options: {', '.join(unknown)}. "
                "Unknown options will raise an error in libthumbor 3.0.",
                DeprecationWarning,
                stacklevel=2,
            )

        if options.get("unsafe", False):
            return unsafe_url(**options)

        return self.generate_new(options)
