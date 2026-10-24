# libthumbor - python extension to thumbor
# https://github.com/thumbor/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""URL composer to create options-based URLs for thumbor encryption."""

# pylint: disable=line-too-long,too-many-branches,too-many-locals,too-many-arguments

import hashlib
import numbers
import re
import warnings

AVAILABLE_HALIGN = ["left", "center", "right"]
AVAILABLE_VALIGN = ["top", "middle", "bottom"]
CROP_ALIASES = ("crop_left", "crop_top", "crop_right", "crop_bottom")
KNOWN_OPTIONS = frozenset(
    (
        "image_url",
        "unsafe",
        "debug",
        "meta",
        "trim",
        "crop",
        *CROP_ALIASES,
        "fit_in",
        "full_fit_in",
        "adaptive_fit_in",
        "adaptive_full_fit_in",
        "width",
        "height",
        "flip",
        "flop",
        "horizontal_flip",
        "vertical_flip",
        "halign",
        "valign",
        "smart",
        "filters",
    )
)


FIT_IN_SEGMENTS = {
    "fit_in": "fit-in",
    "full_fit_in": "full-fit-in",
    "adaptive_fit_in": "adaptive-fit-in",
    "adaptive_full_fit_in": "adaptive-full-fit-in",
}
TRUE_VALUES = frozenset(("1", "true", "yes", "on"))
FALSE_VALUES = frozenset(("0", "false", "no", "off", ""))
TRIM_PATTERN = re.compile(r"(?:(?:top-left|bottom-right)(?::\d+)?|\d+)")


def _int_or_0(value):
    return 0 if value is None else int(value)


def read_flag(options, name):
    """Reads a boolean option, accepting the strings the Django view accepts."""
    value = options.get(name, False)
    if not isinstance(value, str):
        return bool(value)
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ValueError(f"The {name} option must be a boolean.")


def _is_digits(value):
    return isinstance(value, str) and value.isascii() and value.isdigit()


def _is_integer(value):
    return isinstance(value, numbers.Integral) and not isinstance(value, bool)


def _dimension(options, name):
    value = options.get(name)
    if value is None:
        return 0
    if _is_integer(value) or _is_digits(value):
        return int(value)
    if value == "orig":
        return value
    raise ValueError(f'The {name} option must be an integer or "orig".')


def _flipped(dimension):
    # Negating 0 or a string such as "300" or "orig" would drop the sign.
    if isinstance(dimension, int) and dimension:
        return -dimension
    return f"-{dimension or 0}"


def calculate_width_and_height(url_parts, options):
    """Appends width and height information to url"""
    width = _dimension(options, "width")
    height = _dimension(options, "height")

    if read_flag(options, "flip"):
        width = _flipped(width)
    if read_flag(options, "flop"):
        height = _flipped(height)

    if width or height:
        url_parts.append(f"{width}x{height}")


def _crop_value(value):
    if (_is_integer(value) and value >= 0) or _is_digits(value):
        return int(value)
    raise ValueError("The crop values must be non-negative integers.")


def _crop_segment(crop):
    if not crop:
        return None
    try:
        (left, top), (right, bottom) = crop
    except (TypeError, ValueError) as error:
        raise ValueError(
            "The crop option must be a ((left, top), (right, bottom)) pair."
        ) from error
    left, top, right, bottom = (_crop_value(v) for v in (left, top, right, bottom))
    if not (left or top or right or bottom):
        return None
    return f"{left}x{top}:{right}x{bottom}"


def _trim_segment(trim):
    if not trim:
        return None
    if trim is True:
        return "trim"
    if isinstance(trim, str):
        body = trim
    elif isinstance(trim, (tuple, list)) and len(trim) == 2:
        body = ":".join(str(bit) for bit in trim if bit)
    else:
        raise ValueError(
            "The trim option must be True, a string or a (position, tolerance) pair."
        )
    if not body:
        return "trim"
    if not TRIM_PATTERN.fullmatch(body):
        raise ValueError(
            'The trim option accepts "top-left" or "bottom-right" and a tolerance.'
        )
    return f"trim:{body}"


def _filters_segment(filters):
    if not filters:
        return None
    if isinstance(filters, str):
        return f"filters:{filters}"
    try:
        return ":".join(["filters", *filters])
    except TypeError as error:
        raise ValueError("The filters option must be a string or a list.") from error


def url_for(**options):
    """Returns the options path with the image URL replaced by its MD5.

    Deprecated: this was the payload of the encrypted URL format that neither
    libthumbor nor thumbor supports anymore. Use CryptoURL.generate() instead.
    """
    warnings.warn(
        "url_for() is deprecated and will be removed in libthumbor 3.0. It builds "
        "the payload of the encrypted URL format thumbor no longer supports; use "
        "CryptoURL.generate() for signed URLs.",
        DeprecationWarning,
        stacklevel=2,
    )

    url_parts = get_url_parts(**options)
    image_hash = hashlib.md5(
        options["image_url"].encode("utf-8"), usedforsecurity=False
    ).hexdigest()
    url_parts.append(image_hash)

    return "/".join(url_parts)


def unsafe_url(**options):
    """Returns the unsafe url with the specified options"""
    return f"unsafe/{plain_image_url(**options)}"


def plain_image_url(**options):
    url_parts = get_url_parts(**options)
    url_parts.append(options["image_url"])

    return "/".join(url_parts)


def _resolve_aliases(options):
    """Maps the Url.generate_options names, which thumbor-url passes, onto ours."""
    options = dict(options)
    if read_flag(options, "horizontal_flip"):
        options["flip"] = True
    if read_flag(options, "vertical_flip"):
        options["flop"] = True
    crop = [options.pop(name, None) for name in CROP_ALIASES]
    if options.get("crop") is None and any(crop):
        left, top, right, bottom = (value or 0 for value in crop)
        options["crop"] = ((left, top), (right, bottom))
    return options


def get_url_parts(**options):
    if not options.get("image_url"):
        raise ValueError("The image_url argument is mandatory.")

    options = _resolve_aliases(options)
    url_parts = []

    for name in ("debug", "meta"):
        if read_flag(options, name):
            url_parts.append(name)

    for segment in (
        _trim_segment(options.get("trim")),
        _crop_segment(options.get("crop")),
    ):
        if segment:
            url_parts.append(segment)

    calculate_fit_in(options, url_parts)
    calculate_width_and_height(url_parts, options)

    halign = options.get("halign", "center")
    valign = options.get("valign", "middle")

    if halign not in AVAILABLE_HALIGN:
        raise ValueError(
            'Only "left", "center" and "right" are'
            + " valid values for horizontal alignment."
        )
    if valign not in AVAILABLE_VALIGN:
        raise ValueError(
            'Only "top", "middle" and "bottom" are'
            + " valid values for vertical alignment."
        )

    if halign != "center":
        url_parts.append(halign)
    if valign != "middle":
        url_parts.append(valign)

    if read_flag(options, "smart"):
        url_parts.append("smart")

    filters = _filters_segment(options.get("filters"))
    if filters:
        url_parts.append(filters)

    return url_parts


def calculate_fit_in(options, url_parts):
    segments = [
        segment for name, segment in FIT_IN_SEGMENTS.items() if read_flag(options, name)
    ]
    if len(segments) > 1:
        raise ValueError(
            "Only one of fit_in, full_fit_in, adaptive_fit_in and "
            "adaptive_full_fit_in can be set."
        )
    if segments and not (_dimension(options, "width") or _dimension(options, "height")):
        raise ValueError(
            "When using fit-in or full-fit-in, you must specify width and/or height."
        )
    url_parts.extend(segments)


class Url:

    unsafe_or_hash = r"(?:(?:(?P<unsafe>unsafe)|(?P<hash>.+?))/)?"
    debug = r"(?:(?P<debug>debug)/)?"
    meta = r"(?:(?P<meta>meta)/)?"
    trim = r"(?:(?P<trim>trim(?::(?:top-left|bottom-right))?(?::\d+)?)/)?"
    crop = r"(?:(?P<crop_left>\d+)x(?P<crop_top>\d+):(?P<crop_right>\d+)x(?P<crop_bottom>\d+)/)?"
    fit_in = r"(?:(?P<adaptive>adaptive-)?(?P<full>full-)?(?P<fit_in>fit-in)/)?"
    dimensions = r"(?:(?P<horizontal_flip>-)?(?P<width>(?:\d+|orig))?x(?P<vertical_flip>-)?(?P<height>(?:\d+|orig))?/)?"
    halign = r"(?:(?P<halign>left|right|center)/)?"
    valign = r"(?:(?P<valign>top|bottom|middle)/)?"
    smart = r"(?:(?P<smart>smart)/)?"
    filters = r"(?:filters:(?P<filters>.+?\))/)?"
    image = r"(?P<image>.+)"

    compiled_regex = None

    @classmethod
    def regex(cls, has_unsafe_or_hash=True):
        reg = ["/?"]

        if has_unsafe_or_hash:
            reg.append(cls.unsafe_or_hash)
        reg.append(cls.debug)
        reg.append(cls.meta)
        reg.append(cls.trim)
        reg.append(cls.crop)
        reg.append(cls.fit_in)
        reg.append(cls.dimensions)
        reg.append(cls.halign)
        reg.append(cls.valign)
        reg.append(cls.smart)
        reg.append(cls.filters)
        reg.append(cls.image)

        return "".join(reg)

    @classmethod
    def parse_decrypted(cls, url):
        """Returns the options in a thumbor path, or None if it cannot be parsed"""
        if cls.compiled_regex:
            reg = cls.compiled_regex
        else:
            reg = cls.compiled_regex = re.compile(cls.regex(has_unsafe_or_hash=False))

        result = reg.match(url)

        if not result:
            return None

        try:
            return cls._values_from_match(result.groupdict())
        except ValueError:
            return None

    @classmethod
    def _values_from_match(cls, result):
        adaptive = (result.get("adaptive", "") or "").startswith("adaptive")
        full = (result.get("full", "") or "").startswith("full")

        return {
            "debug": result["debug"] == "debug",
            "meta": result["meta"] == "meta",
            "trim": result["trim"],
            "crop": {
                "left": _int_or_0(result["crop_left"]),
                "top": _int_or_0(result["crop_top"]),
                "right": _int_or_0(result["crop_right"]),
                "bottom": _int_or_0(result["crop_bottom"]),
            },
            "adaptive": adaptive,
            "full": full,
            "fit_in": result["fit_in"] == "fit-in",
            "width": result["width"] == "orig" and "orig" or _int_or_0(result["width"]),
            "height": result["height"] == "orig"
            and "orig"
            or _int_or_0(result["height"]),
            "horizontal_flip": result["horizontal_flip"] == "-",
            "vertical_flip": result["vertical_flip"] == "-",
            "halign": result["halign"] or "center",
            "valign": result["valign"] or "middle",
            "smart": result["smart"] == "smart",
            "filters": result["filters"] or "",
            "image": "image" in result and result["image"] or None,
        }

    @classmethod  # NOQA
    def generate_options(  # pylint: disable=too-many-positional-arguments
        cls,
        debug=False,
        width=0,
        height=0,
        smart=False,
        meta=False,
        trim=None,
        adaptive=False,
        full=False,
        fit_in=False,
        horizontal_flip=False,
        vertical_flip=False,
        halign="center",
        valign="middle",
        crop_left=None,
        crop_top=None,
        crop_right=None,
        crop_bottom=None,
        filters=None,
    ):
        url = []

        if debug:
            url.append("debug")

        if meta:
            url.append("meta")

        if trim:
            if isinstance(trim, bool):
                url.append("trim")
            else:
                url.append(f"trim:{trim}")

        crop = crop_left or crop_top or crop_right or crop_bottom
        if crop:
            url.append(f"{crop_left}x{crop_top}:{crop_right}x{crop_bottom}")

        if fit_in:
            fit_ops = []
            if adaptive:
                fit_ops.append("adaptive")
            if full:
                fit_ops.append("full")
            fit_ops.append("fit-in")
            url.append("-".join(fit_ops))

        if horizontal_flip:
            width = f"-{width}"
        if vertical_flip:
            height = f"-{height}"

        if width or height:
            url.append(f"{width}x{height}")

        if halign != "center":
            url.append(halign)
        if valign != "middle":
            url.append(valign)

        if smart:
            url.append("smart")

        if filters:
            url.append(f"filters:{filters}")

        return "/".join(url)
