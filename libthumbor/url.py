# libthumbor - python extension to thumbor
# https://github.com/thumbor/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

"""URL composer to create options-based URLs for thumbor encryption."""

# pylint: disable=line-too-long,too-many-branches,too-many-locals,too-many-arguments

import hashlib
import re
import warnings
from dataclasses import dataclass

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


def _dimension(options, name):
    value = options.get(name)
    if value is None:
        return 0
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if _is_digits(value) or value == "orig":
        return value
    raise ValueError(f'The {name} option must be an integer or "orig".')


def _signed(dimension, flipped):
    # A negative number has always meant a flipped dimension.
    if isinstance(dimension, int) and dimension < 0:
        return -dimension, not flipped
    return dimension, flipped


def _crop_value(value):
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    if _is_digits(value):
        return int(value)
    raise ValueError("The crop values must be non-negative integers.")


def _crop(crop):
    if not crop:
        return None
    (left, top), (right, bottom) = crop
    sides = tuple(_crop_value(value) for value in (left, top, right, bottom))
    return sides if any(sides) else None


def _trim(trim):
    """Returns the text after "trim:", "" for a plain trim, or None for no trim."""
    if isinstance(trim, bool) or trim is None:
        return "" if trim else None
    if isinstance(trim, str):
        body = trim
    elif isinstance(trim, (tuple, list)) and len(trim) == 2:
        body = ":".join(str(bit) for bit in trim if bit)
    else:
        raise ValueError(
            "The trim option must be True, a string or a (position, tolerance) pair."
        )
    if body and not TRIM_PATTERN.fullmatch(body):
        raise ValueError(
            'The trim option accepts "top-left" or "bottom-right" and a tolerance.'
        )
    return body


def _filters(filters):
    if not filters:
        return None
    if isinstance(filters, str):
        return filters
    return ":".join(filters)


def _check_alignment(halign, valign):
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


@dataclass(frozen=True)
class _Path:  # pylint: disable=too-many-instance-attributes
    """The options part of a thumbor path, one field per segment of its regex.

    CryptoURL, Url.generate_options and Url.parse_decrypted all go through it,
    so the three cannot disagree on how a path is written.
    """

    debug: bool = False
    meta: bool = False
    trim: str | None = None
    crop: tuple[int, int, int, int] | None = None
    fit_in: str | None = None
    width: int | str = 0
    height: int | str = 0
    horizontal_flip: bool = False
    vertical_flip: bool = False
    halign: str = "center"
    valign: str = "middle"
    smart: bool = False
    filters: str | None = None

    def segments(self):
        parts = [name for name in ("debug", "meta") if getattr(self, name)]
        if self.trim is not None:
            parts.append(f"trim:{self.trim}" if self.trim else "trim")
        if self.crop is not None:
            left, top, right, bottom = self.crop
            parts.append(f"{left}x{top}:{right}x{bottom}")
        if self.fit_in:
            parts.append(self.fit_in)
        if self.width or self.height or self.horizontal_flip or self.vertical_flip:
            width = f"{'-' if self.horizontal_flip else ''}{self.width}"
            height = f"{'-' if self.vertical_flip else ''}{self.height}"
            parts.append(f"{width}x{height}")
        parts.extend(
            segment
            for segment, default in ((self.halign, "center"), (self.valign, "middle"))
            if segment != default
        )
        if self.smart:
            parts.append("smart")
        if self.filters:
            parts.append(f"filters:{self.filters}")
        return parts


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


def _fit_in(options):
    segments = [
        segment for name, segment in FIT_IN_SEGMENTS.items() if read_flag(options, name)
    ]
    if len(segments) > 1:
        raise ValueError(
            "Only one of fit_in, full_fit_in, adaptive_fit_in and "
            "adaptive_full_fit_in can be set."
        )
    if segments and not (options.get("width") or options.get("height")):
        raise ValueError(
            "When using fit-in or full-fit-in, you must specify width and/or height."
        )
    return segments[0] if segments else None


def _fit_in_with_modifiers(options):
    """Reads fit-in the way Url.generate_options spells it: a flag plus modifiers."""
    adaptive = read_flag(options, "adaptive")
    full = read_flag(options, "full")
    if not read_flag(options, "fit_in"):
        if adaptive or full:
            raise ValueError("The adaptive and full options require fit_in.")
        return None
    return "adaptive-" * adaptive + "full-" * full + "fit-in"


def _build_path(options, read_fit_in):
    options = _resolve_aliases(options)
    debug = read_flag(options, "debug")
    meta = read_flag(options, "meta")
    trim = _trim(options.get("trim"))
    crop = _crop(options.get("crop"))
    fit_in = read_fit_in(options)
    width = _dimension(options, "width")
    height = _dimension(options, "height")
    width, horizontal_flip = _signed(width, read_flag(options, "flip"))
    height, vertical_flip = _signed(height, read_flag(options, "flop"))
    halign = options.get("halign", "center")
    valign = options.get("valign", "middle")
    _check_alignment(halign, valign)
    return _Path(
        debug=debug,
        meta=meta,
        trim=trim,
        crop=crop,
        fit_in=fit_in,
        width=width,
        height=height,
        horizontal_flip=horizontal_flip,
        vertical_flip=vertical_flip,
        halign=halign,
        valign=valign,
        smart=read_flag(options, "smart"),
        filters=_filters(options.get("filters")),
    )


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


def get_url_parts(**options):
    if not options.get("image_url"):
        raise ValueError("The image_url argument is mandatory.")

    return _build_path(options, _fit_in).segments()


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

        groups = result.groupdict()
        try:
            path = cls._path_from_match(groups)
        except ValueError:
            return None
        return cls._parsed(path, groups["image"])

    @staticmethod
    def _path_from_match(groups):
        crop = [groups[f"crop_{side}"] for side in ("left", "top", "right", "bottom")]
        fit_in = None
        if groups["fit_in"]:
            fit_in = f"{groups['adaptive'] or ''}{groups['full'] or ''}fit-in"
        width, height = (
            groups[name] if groups[name] == "orig" else _int_or_0(groups[name])
            for name in ("width", "height")
        )
        return _Path(
            debug=groups["debug"] == "debug",
            meta=groups["meta"] == "meta",
            trim=None if groups["trim"] is None else groups["trim"].partition(":")[2],
            crop=None if crop[0] is None else tuple(int(side) for side in crop),
            fit_in=fit_in,
            width=width,
            height=height,
            horizontal_flip=groups["horizontal_flip"] == "-",
            vertical_flip=groups["vertical_flip"] == "-",
            halign=groups["halign"] or "center",
            valign=groups["valign"] or "middle",
            smart=groups["smart"] == "smart",
            filters=groups["filters"],
        )

    @staticmethod
    def _parsed(path, image):
        trim = None
        if path.trim is not None:
            trim = f"trim:{path.trim}" if path.trim else "trim"
        fit_in = path.fit_in or ""
        return {
            "debug": path.debug,
            "meta": path.meta,
            "trim": trim,
            "crop": dict(
                zip(("left", "top", "right", "bottom"), path.crop or (0, 0, 0, 0))
            ),
            "adaptive": fit_in.startswith("adaptive-"),
            "full": "full-" in fit_in,
            "fit_in": bool(fit_in),
            "width": path.width,
            "height": path.height,
            "horizontal_flip": path.horizontal_flip,
            "vertical_flip": path.vertical_flip,
            "halign": path.halign,
            "valign": path.valign,
            "smart": path.smart,
            "filters": path.filters or "",
            "image": image,
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
        options = {
            "debug": debug,
            "width": width,
            "height": height,
            "smart": smart,
            "meta": meta,
            "trim": trim,
            "adaptive": adaptive,
            "full": full,
            "fit_in": fit_in,
            "horizontal_flip": horizontal_flip,
            "vertical_flip": vertical_flip,
            "halign": halign,
            "valign": valign,
            "crop_left": crop_left,
            "crop_top": crop_top,
            "crop_right": crop_right,
            "crop_bottom": crop_bottom,
            "filters": filters,
        }
        return "/".join(_build_path(options, _fit_in_with_modifiers).segments())
