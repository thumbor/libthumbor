# libthumbor

`libthumbor` is a Python library for composing, signing, and parsing
[thumbor](https://github.com/thumbor/thumbor) image URLs.

It helps applications generate thumbor-compatible URLs safely, keep signing
logic in one place, and reuse the same URL-building rules across services.

## Highlights

- Generate signed thumbor URLs with `CryptoURL`
- Compose transformation paths with `Url.generate_options()`
- Parse decrypted thumbor paths with `Url.parse_decrypted()`
- Validate signatures with the bundled signer implementation
- Use the included Django view for simple URL generation endpoints
- Type hints for the public API, checked by mypy (`py.typed`)

## Requirements

- Python 3.11+

## Installation

```bash
pip install libthumbor
```

For local development, use:

```bash
make setup
```

## Quick Start

Generate a signed thumbor URL:

```python
from libthumbor import CryptoURL

crypto = CryptoURL(key="my-security-key")

url = crypto.generate(
    width=300,
    height=200,
    smart=True,
    image_url="images.example.com/photo.jpg",
)

print(url)
```

The generated URL follows thumbor's signed URL format:

```text
/<signature>/300x200/smart/images.example.com/photo.jpg
```

Generate an unsafe URL when signing is intentionally disabled:

```python
from libthumbor.crypto import CryptoURL

crypto = CryptoURL(key="my-security-key")

url = crypto.generate(
    unsafe=True,
    width=300,
    height=200,
    image_url="images.example.com/photo.jpg",
)

print(url)
```

Output structure:

```text
unsafe/300x200/images.example.com/photo.jpg
```

## Image URLs From Untrusted Input

`CryptoURL` signs `image_url` exactly as given, and thumbor reads options from
the whole path. When the value comes from a user or a request, an `image_url`
such as `filters:format(png)/photo.jpg` adds a `filters` option to the signed
URL. Characters a browser percent-encodes in a path (spaces, non-ASCII
letters, `?`, `#`) break the signature instead, because thumbor checks it
against the path it receives rather than the string that was signed.

Percent-encode such values before signing, slashes included:

```python
from urllib.parse import quote

from libthumbor import CryptoURL

crypto = CryptoURL(key="my-security-key")

url = crypto.generate(
    width=300,
    height=200,
    image_url=quote("images.example.com/photo of the day.jpg", safe=""),
)
```

```text
/<signature>/300x200/images.example.com%2Fphoto%20of%20the%20day.jpg
```

The `safe=""` matters: `quote()` keeps `/` by default, which still lets a
value such as `smart/photo.jpg` add the `smart` option.

thumbor decodes the image URL once before loading it, so the file and HTTP
loaders receive the original value and `ALLOWED_SOURCES` still applies to it.
Pass the decoded value: a path that is already percent-encoded, such as
`photo%20of%20the%20day.jpg` taken from a request URL, would be encoded again,
and thumbor would look for a file with a literal `%20` in its name. Run such
values through `unquote()` first.

The encoded path differs from the unencoded one (`/` becomes `%2F`), so
switching existing callers produces new URLs; the ones generated before keep
working.

## URL Composition

If you want only the thumbor transformation path, use `Url.generate_options()`:

```python
from libthumbor import Url

path = Url.generate_options(
    width=300,
    height=200,
    smart=True,
    fit_in=True,
    halign="left",
    valign="top",
    filters="brightness(10):contrast(5)",
)

print(path)
```

Output:

```text
fit-in/300x200/left/top/smart/filters:brightness(10):contrast(5)
```

## Parsing Existing URLs

`Url.parse_decrypted()` parses a thumbor path without the leading signature:

```python
from libthumbor import Url

data = Url.parse_decrypted(
    "meta/10x20:200x300/adaptive-full-fit-in/-400x-300/"
    "left/top/smart/filters:brightness(100)/images.example.com/photo.jpg"
)

print(data["width"])
print(data["height"])
print(data["smart"])
print(data["image"])
```

## Supported Options

The library supports the transformation pieces covered by the test suite and
thumbor-compatible URL composer:

- `width`, `height`
- `crop=((left, top), (right, bottom))`, or `crop_left`, `crop_top`, `crop_right`,
  `crop_bottom` as `thumbor-url` passes them
- `fit_in`, `full_fit_in`
- `adaptive_fit_in`, `adaptive_full_fit_in`
- `flip`, `flop`, also accepted as `horizontal_flip` and `vertical_flip`
- `halign` with `left`, `center`, `right`
- `valign` with `top`, `middle`, `bottom`
- `smart`
- `trim`
- `filters`
- `meta`
- `debug`
- `unsafe`

## Signature Utilities

The package also exposes the bundled signer implementation:

```python
from libthumbor import Signer

signer = Signer("my-security-key")
signature = signer.signature("300x200/image.jpg").decode("ascii")
```

This is useful when you need lower-level signing or signature validation
outside `CryptoURL`.

## Django Integration

`libthumbor` ships with a simple Django view that returns a generated thumbor
URL as plain text. Install it with the `django` extra, which declares the
supported range (Django 5.2 LTS and 6.x):

```bash
pip install "libthumbor[django]"
```

Settings:

```python
THUMBOR_SECURITY_KEY = "my-security-key"
THUMBOR_SERVER = "http://localhost:8888/"
```

URL config:

```python
from django.urls import include, path

urlpatterns = [
    path("", include("libthumbor.django.urls")),
]
```

Example request:

```text
GET /gen_url/?image_url=images.example.com/photo.jpg&width=300&height=200
```

The view only reads a fixed set of query parameters: `image_url`, `width`,
`height`, `halign`, `valign`, `filters` (colon-separated), the crop
coordinates and the boolean flags (`smart`, `meta`, `trim`, `flip`, `flop`
and the `fit_in` variants, accepting `1`/`0`, `true`/`false`, `yes`/`no`,
`on`/`off`). Anything else, including `unsafe`, is ignored. Error responses
are `text/plain` and never echo the submitted values.

Treat the view as a signing oracle: anyone who can reach it obtains a valid
signature for any `image_url`, which makes the thumbor security key
irrelevant for those callers. Put it behind authentication and restrict the
origins thumbor is allowed to load (`ALLOWED_SOURCES`) before exposing it.
The view raises `ImproperlyConfigured` when `THUMBOR_SECURITY_KEY` is unset.

To restrict what the view signs, point `THUMBOR_URL_VALIDATOR` at a callable
or at its dotted path. It runs after the query string is parsed and before
signing, and receives the request and the parsed options. Raising
`InvalidParameter` answers 400 with its message, which must not echo the
submitted values, and raising `PermissionDenied` answers 403. Any other
exception propagates as a 500, so guard calls that can fail on user input.
Because the query string is parsed first, a malformed parameter answers 400
even when the validator would deny the request; wrap the view with
`login_required` when that distinction matters:

```python
from urllib.parse import urlsplit

from django.core.exceptions import PermissionDenied

from libthumbor.django.views import InvalidParameter


def validate_thumbor_url(request, options):
    if not request.user.is_authenticated:
        raise PermissionDenied
    image_url = options.get("image_url", "")
    if "://" not in image_url:
        image_url = f"http://{image_url}"
    try:
        hostname = urlsplit(image_url).hostname
    except ValueError:
        hostname = None
    if hostname != "images.example.com":
        raise InvalidParameter("Images must come from images.example.com.")
    if options.get("filters"):
        raise InvalidParameter("Filters are not allowed.")
```

```python
THUMBOR_URL_VALIDATOR = "myproject.thumbor.validate_thumbor_url"
```

## Development

Install dependencies:

```bash
make setup
```

Install the local git hooks:

```bash
make pre-commit-install
```

Run the main validation flow:

```bash
make test
```

Run individual checks:

```bash
make unit
make coverage
make black
make flake8
make isort-check
make pylint
make mypy
make pre-commit
```

## Testing and Compatibility Notes

- The project targets Python 3.11 and newer.
- URL signing is compatibility-sensitive. Changes in signing or URL composition
  should be reviewed carefully.
- If you change URL semantics, verify that previously generated signed URLs
  still behave as expected.

## License

MIT
