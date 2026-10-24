# libthumbor - python extension to thumbor
# https://github.com/thumbor/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""Encrypted URLs for thumbor encryption."""

import warnings

from libthumbor.url import KNOWN_OPTIONS, plain_image_url, read_flag, unsafe_url
from libthumbor.url_signers.base64_hmac_sha1 import UrlSigner


class CryptoURL:
    """Class responsible for generating encrypted URLs for thumbor"""

    def __init__(self, key):
        """
        Initializes the encryptor with the proper key
        :param key: secret key to use for hashing.
        """

        self.signer = UrlSigner(key)
        self.key = self.signer.security_key

    def generate_new(self, options):
        url = plain_image_url(**options)
        signature = self.signer.signature(url).decode("ascii")

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

        if read_flag(options, "unsafe"):
            return unsafe_url(**options)

        return self.generate_new(options)
