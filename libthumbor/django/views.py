# libthumbor - python extension to thumbor
# https://github.com/thumbor/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""Generic view for create thumbor encrypted urls."""

import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed

from libthumbor.crypto import CryptoURL
from libthumbor.url import read_flag

logger = logging.getLogger(__name__)

INVALID_PARAMS_MESSAGE = "Invalid thumbor URL parameters."
DEFAULT_THUMBOR_SERVER = "http://localhost:8888/"

STRING_PARAMS = ("halign", "valign")
INTEGER_PARAMS = ("width", "height")
CROP_PARAMS = ("crop_left", "crop_top", "crop_right", "crop_bottom")
FLAG_PARAMS = (
    "smart",
    "meta",
    "trim",
    "flip",
    "flop",
    "fit_in",
    "full_fit_in",
    "adaptive_fit_in",
    "adaptive_full_fit_in",
)


class InvalidParameter(ValueError):
    """A query string parameter could not be converted to a thumbor option.

    ``message`` is sent to the client as is, so it must never include the
    submitted value.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def get_security_key():
    key = getattr(settings, "THUMBOR_SECURITY_KEY", None)
    if not key:
        raise ImproperlyConfigured("The THUMBOR_SECURITY_KEY setting is required.")
    return key


def get_thumbor_server():
    server = getattr(settings, "THUMBOR_SERVER", DEFAULT_THUMBOR_SERVER)
    return server.rstrip("/") + "/"


def parse_integer(name, value):
    try:
        return int(value)
    except ValueError as error:
        raise InvalidParameter(f"The {name} value is not an integer.") from error


def parse_flag(name, value):
    try:
        return read_flag({name: value}, name)
    except ValueError as error:
        raise InvalidParameter(f"The {name} value is not a boolean.") from error


def parse_crop(query):
    present = [name for name in CROP_PARAMS if name in query]
    if not present:
        return None
    if len(present) != len(CROP_PARAMS):
        raise InvalidParameter(
            "Missing values for cropping. Expected all 'crop_left', 'crop_top', "
            "'crop_right' and 'crop_bottom' values."
        )
    try:
        left, top, right, bottom = (int(query[name]) for name in CROP_PARAMS)
    except ValueError as error:
        raise InvalidParameter(
            "Invalid values for cropping. Expected all 'crop_left', 'crop_top', "
            "'crop_right' and 'crop_bottom' to be integers."
        ) from error
    if min(left, top, right, bottom) < 0:
        raise InvalidParameter(
            "Invalid values for cropping. Expected non-negative integers."
        )
    return ((left, top), (right, bottom))


def parse_options(query):
    options = {}
    if query.get("image_url", "").strip():
        options["image_url"] = query["image_url"]
    for name in STRING_PARAMS:
        if name in query:
            options[name] = query[name]
    for name in INTEGER_PARAMS:
        if name in query:
            options[name] = parse_integer(name, query[name])
    for name in FLAG_PARAMS:
        if name in query:
            options[name] = parse_flag(name, query[name])
    if "filters" in query:
        options["filters"] = [part for part in query["filters"].split(":") if part]
    crop = parse_crop(query)
    if crop is not None:
        options["crop"] = crop
    return options


def generate_url(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"], content_type="text/plain")

    crypto = CryptoURL(get_security_key())

    try:
        options = parse_options(request.GET)
    except InvalidParameter as error:
        logger.warning("Invalid thumbor URL parameters: %s", error)
        return HttpResponseBadRequest(error.message, content_type="text/plain")

    try:
        url = crypto.generate(**options)
    except (ValueError, KeyError) as error:
        logger.warning("Invalid thumbor URL parameters: %s", error)
        return HttpResponseBadRequest(INVALID_PARAMS_MESSAGE, content_type="text/plain")

    return HttpResponse(
        get_thumbor_server() + url.strip("/"), content_type="text/plain"
    )
