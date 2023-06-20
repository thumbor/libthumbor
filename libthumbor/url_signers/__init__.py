#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from six import text_type
import secrets


class BaseUrlSigner:
    def __init__(self, security_key):
        if isinstance(security_key, text_type):
            security_key = security_key.encode("utf-8")
        self.security_key = security_key

    def validate(self, actual_signature, url):
        url_signature = self.signature(url)
        return secrets.compare_digest(url_signature, actual_signature)

    def signature(self, url):
        raise NotImplementedError()
