#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""libthumbor is the library used to access thumbor's images in python"""

from pkg_resources import DistributionNotFound, get_distribution

from libthumbor.crypto import CryptoURL  # NOQA
from libthumbor.url import Url  # NOQA
from libthumbor.url_signers.base64_hmac_sha1 import UrlSigner as Signer  # NOQA

__project__ = "libthumbor"

try:
    __version__ = get_distribution(__project__).version
except DistributionNotFound:
    # Returns a local version. For tests.
    __version__ = "{}-local".format(__project__)
