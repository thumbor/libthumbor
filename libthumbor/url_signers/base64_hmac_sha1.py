# -*- coding: utf-8 -*-

import base64
import hashlib
import hmac

from six import text_type

from libthumbor.url_signers import BaseUrlSigner


class UrlSigner(BaseUrlSigner):
    """Validate urls and sign them using base64 hmac-sha1
    """

    def signature(self, url):
        return base64.urlsafe_b64encode(
            hmac.new(
                self.security_key, text_type(url).encode('utf-8'), hashlib.sha1
            ).digest()
        )
