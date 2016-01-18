#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import base64
import hashlib
import hmac


from six import text_type


class Signer:
    def __init__(self, security_key):
        if isinstance(security_key, text_type):
            security_key = security_key.encode('utf-8')
        self.security_key = security_key

    def validate(self, actual_signature, url):
        url_signature = self.signature(url)
        return url_signature == actual_signature

    def signature(self, url):
        return base64.urlsafe_b64encode(hmac.new(self.security_key, text_type(url).encode('utf-8'), hashlib.sha1).digest())
