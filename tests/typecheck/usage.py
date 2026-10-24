# libthumbor - python extension to thumbor
# https://github.com/thumbor/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

"""The public API as a type checker sees it.

mypy checks this file together with the package. The correct calls must keep
type-checking and the wrong ones must keep being rejected: strict mode warns
on an unused ``type: ignore``, so a loosened annotation fails here too.
"""

from collections.abc import Mapping
from typing import Any

from libthumbor import CryptoURL, Signer, Url
from libthumbor.url_signers import BaseUrlSigner


class PlainSigner(BaseUrlSigner):
    """A custom signer, the kind thumbor loads through its URL_SIGNER setting."""

    def signature(self, url: str) -> bytes:
        return url.encode("utf-8")


def sign(key: str | bytes | bytearray) -> str:
    return CryptoURL(key=key).generate(
        width=300, height="orig", smart=True, filters=["blur(2)"], image_url="a.jpg"
    )


def sign_mapping(key: str, options: Mapping[str, Any]) -> str:
    return CryptoURL(key).generate_new(options)


def verify(key: str | bytes | bytearray, path: str) -> bool:
    signer = Signer(key)
    signature: bytes = signer.signature(path)
    return signer.validate(signature, path)


def verify_custom(path: str) -> bool:
    signer = PlainSigner("secret")
    return signer.validate(signer.signature(path), path)


def route() -> str:
    pattern: str = Url.regex()
    return pattern + Url.regex(has_unsafe_or_hash=False)


def compose() -> str:
    return Url.generate_options(
        width=300, height="orig", trim=("top-left", 10), filters=["blur(2)"]
    )


def parse(path: str) -> dict[str, Any] | None:
    return Url.parse_decrypted(path)


def rejected() -> None:
    _ = CryptoURL(key=123)  # type: ignore[arg-type]
    _ = Url.parse_decrypted(5)  # type: ignore[arg-type]
    _ = Url.generate_options(width=1.5)  # type: ignore[arg-type]
    _ = Url.generate_options(trim=["top-left", 10])  # type: ignore[arg-type]
    _ = Url.regex(has_unsafe_or_hash="no")  # type: ignore[arg-type]
    signature: str = Signer("secret").signature("a.jpg")  # type: ignore[assignment]
    _ = signature
