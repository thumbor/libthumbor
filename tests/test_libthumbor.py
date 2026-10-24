# libthumbor - python extension to thumbor
# https://github.com/thumbor/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

import re
from urllib.parse import quote

from libthumbor import CryptoURL, Signer, Url


def test_usage_new_format():
    key = "my-security-key"
    image = "s.glbimg.com/et/bb/f/original/2011/03/24/VN0JiwzmOw0b0lg.jpg"

    thumbor_signer = Signer(key)
    thumbor_url = Url.generate_options(
        width=300,
        height=200,
        smart=True,
        adaptive=False,
        fit_in=False,
        horizontal_flip=False,
        vertical_flip=False,
        crop_left=0,
        crop_top=0,
        crop_right=0,
        crop_bottom=0,
        filters=[],
    )
    thumbor_url = (f"{thumbor_url}/{image}").lstrip("/")
    signature = thumbor_signer.signature(thumbor_url).decode("ascii")
    thumbor_url = f"/{signature}/{thumbor_url}"

    crypto = CryptoURL(key=key)
    url = crypto.generate(width=300, height=200, smart=True, image_url=image)

    assert url == thumbor_url


def test_thumbor_can_decrypt_lib_thumbor_generated_url_new_format():
    key = "my-security-key"
    image = "s.glbimg.com/et/bb/f/original/2011/03/24/VN0JiwzmOw0b0lg.jpg"
    thumbor_signer = Signer(key)

    crypto = CryptoURL(key=key)

    url = crypto.generate(width=300, height=200, smart=True, image_url=image)

    reg = "/([^/]+)/(.+)"
    signature, url = re.match(reg, url).groups()

    assert thumbor_signer.validate(signature.encode("utf-8"), url)


def test_percent_encoded_image_url_is_not_parsed_as_options():
    image = quote("smart/filters:format(png)/a.jpg", safe="")
    crypto = CryptoURL(key="my-security-key")

    url = crypto.generate(width=300, height=200, image_url=image)
    match = re.match(Url.regex(), url)

    assert match["smart"] is None
    assert match["filters"] is None
    assert match["image"] == image
