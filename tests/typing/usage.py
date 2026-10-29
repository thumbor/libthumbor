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

from libthumbor import CryptoURL, ParsedUrl, Signer, Url, UrlOptions
from libthumbor.url_signers import BaseUrlSigner


class PlainSigner(BaseUrlSigner):
    """A custom signer, the kind thumbor loads through its URL_SIGNER setting."""

    def signature(self, url: str) -> bytes:
        return url.encode("utf-8")


def sign(key: str | bytes | bytearray) -> str:
    return CryptoURL(key=key).generate(
        width=300, height="orig", smart=True, filters=["blur(2)"], image_url="a.jpg"
    )


def sign_typed(key: str, options: UrlOptions) -> str:
    return CryptoURL(key).generate(**options)


def sign_untyped(key: str, options: dict[str, Any]) -> str:
    """thumbor-url builds its options as a plain dict."""
    return CryptoURL(key).generate(**options)


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


def parse(path: str) -> ParsedUrl | None:
    return Url.parse_decrypted(path)


def parse_as_mapping(path: str) -> Mapping[str, Any] | None:
    return Url.parse_decrypted(path)


def cropped_width(path: str) -> int:
    parsed = Url.parse_decrypted(path)
    if parsed is None:
        return 0
    return parsed["crop"]["right"] - parsed["crop"]["left"]


def rejected() -> None:
    _ = CryptoURL(key=123)  # type: ignore[arg-type]
    _ = Url.parse_decrypted(5)  # type: ignore[arg-type]
    _ = Url.generate_options(width=1.5)  # type: ignore[arg-type]
    _ = Url.generate_options(trim=["top-left", 10])  # type: ignore[arg-type]
    _ = Url.regex(has_unsafe_or_hash="no")  # type: ignore[arg-type]
    _ = CryptoURL("k").generate(image_url="a.jpg", widht=300)  # type: ignore[call-arg]
    _ = CryptoURL("k").generate(width=300)  # type: ignore[call-arg]
    preset = {"width": 300, "height": 200}
    _ = CryptoURL("k").generate(image_url="a.jpg", **preset)  # type: ignore[arg-type]
    signature: str = Signer("secret").signature("a.jpg")  # type: ignore[assignment]
    _ = signature
    parsed = Url.parse_decrypted("a.jpg")
    if parsed is not None:
        _ = parsed["widht"]  # type: ignore[typeddict-item]
