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

## Requirements

- Python 3.10+

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
- `crop=((left, top), (right, bottom))`
- `fit_in`, `full_fit_in`
- `adaptive_fit_in`, `adaptive_full_fit_in`
- `flip`, `flop`
- `halign` with `left`, `center`, `right`
- `valign` with `top`, `middle`, `bottom`
- `smart`
- `trim`
- `filters`
- `meta`
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
URL as plain text.

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
make pre-commit
```

## Testing and Compatibility Notes

- The project targets Python 3.10 and newer.
- URL signing is compatibility-sensitive. Changes in signing or URL composition
  should be reviewed carefully.
- If you change URL semantics, verify that previously generated signed URLs
  still behave as expected.

## License

MIT
