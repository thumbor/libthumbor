# Contributing

Want to contribute to `libthumbor`? Welcome aboard.

This guide covers the basics for setting up your environment, validating
changes, and preparing a pull request.

## Getting Started

Fork the repository and clone your fork locally. If you need a refresher on
that workflow, GitHub's fork documentation is a good place to start:
<https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo>.

## Dependencies

Use [uv](https://docs.astral.sh/uv/) so your local environment matches the
project's tooling and CI.

- Python 3.11 or newer
- uv

Install the project and development dependencies with the following
command. uv reads `.python-version` and installs that interpreter if it is
not available yet:

```bash
make setup
```

## Running Tests

Run the full local validation flow with:

```bash
make test
```

You can also run individual targets when you only need part of the suite:

```bash
make unit
make coverage
make black
make flake8
make isort-check
make pylint
```

The default environment uses Django 5.2 LTS. To run the suite against Django
6, which needs Python 3.12 or newer, sync the `django6` group instead and
keep `uv run` from syncing back to the default groups:

```bash
uv sync --python 3.12 --no-default-groups --group dev --group django6
UV_NO_SYNC=1 make unit
```

## Pull Requests

Before opening a pull request:

- Rebase your branch on top of the latest `master`
- Run the relevant test and lint targets locally
- Keep the change focused and update tests when behavior changes

If you want to track the upstream repository as an extra remote:

```bash
git remote add libthumbor https://github.com/thumbor/libthumbor.git
```

To update your branch with upstream `master`:

```bash
git pull libthumbor master
```

If that pull brings in changes, run the test suite again before opening your
pull request.
