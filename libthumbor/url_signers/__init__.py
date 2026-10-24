# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import hmac


def _as_bytes(value: str | bytes | bytearray) -> bytes | bytearray:
    if isinstance(value, str):
        return value.encode("utf-8")
    return value


class BaseUrlSigner:
    def __init__(self, security_key: str | bytes | bytearray) -> None:
        if isinstance(security_key, str):
            security_key = security_key.encode("utf-8")
        if not isinstance(security_key, (bytes, bytearray)):
            raise TypeError(
                "security_key must be str, bytes or bytearray, "
                f"not {type(security_key).__name__}"
            )
        self.security_key: bytes | bytearray = security_key

    def validate(self, actual_signature: object, url: str) -> bool:
        if not isinstance(actual_signature, (str, bytes, bytearray)):
            return False
        return hmac.compare_digest(
            _as_bytes(self.signature(url)), _as_bytes(actual_signature)
        )

    def signature(self, url: str) -> bytes:
        raise NotImplementedError()
