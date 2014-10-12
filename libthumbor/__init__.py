#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

'''libthumbor is the library used to access thumbor's images in python'''

from pkg_resources import get_distribution

__version__ = get_distribution('libthumbor').version

from libthumbor.crypto import CryptoURL
