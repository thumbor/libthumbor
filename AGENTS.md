# AGENTS.md

libthumbor is a Python library for composing and signing thumbor image URLs.
It provides helpers for secure URL generation, URL parsing, and integration
points that other applications can use to talk to thumbor safely.

## Dev environment setup

- **Prerequisites:** Python 3.7+ and Poetry
- Install project and development dependencies:

  ```
  make setup
  ```

  Equivalent to: `poetry install`

- If you prefer running commands directly, use `poetry run ...` so the virtual
  environment stays consistent with CI and local development.

## Running tests

- Full local validation flow:

  ```
  make test
  ```

- Individual targets:

  ```
  make unit
  make coverage
  make flake8
  make pylint
  ```

- The test suite runs with `pytest` and collects coverage for the
  `libthumbor` package.

## Code style

- **Formatter:** `black` with line length 88 and Python 3.7 target, configured in
  [pyproject.toml](/home/metal/work/libthumbor/pyproject.toml).
- **Linter:** `flake8` with max complexity 20, configured in
  [.flake8](/home/metal/work/libthumbor/.flake8).
- **Static analysis:** `pylint`, configured in
  [.pylintrc](/home/metal/work/libthumbor/.pylintrc).
- Primary workflow commands live in the
  [Makefile](/home/metal/work/libthumbor/Makefile); prefer them over ad hoc
  shell commands when possible.

## Project structure

```
libthumbor/              <- main package
  __init__.py            <- package exports
  crypto.py              <- secure URL generation helpers
  url.py                 <- URL composer and parsing utilities
tests/                   <- pytest suite
  test_cryptourl.py      <- signing and encrypted URL behavior
  test_libthumbor.py     <- package-level behavior
  test_url.py            <- URL parsing and composition
  test_url_composer.py   <- URL builder coverage
  test_generic_views.py  <- Django integration coverage
README.md                <- project overview and usage example
CONTRIBUTING             <- legacy contribution notes
Makefile                 <- common setup, test, and lint tasks
pyproject.toml           <- Poetry metadata and tool configuration
```

## Contribution guidelines

- Keep changes focused and update tests whenever behavior changes.
- Prefer `make test` before opening a PR, and at minimum run the target that
  covers the code you changed.
- `CONTRIBUTING` contains older workflow guidance; when in doubt, follow the
  current Poetry-based commands defined in the Makefile.
- New work should target `master` unless the maintainers document a different
  release branch strategy.

## Security considerations

- Treat the thumbor signing key as sensitive secret material.
- Changes in `crypto.py` or `url.py` can affect signature compatibility and
  should be reviewed carefully.
- Avoid weakening or bypassing signed URL generation in examples or helper
  functions.
- If you change URL semantics, confirm existing signed URLs still behave as
  expected or document the compatibility impact.
