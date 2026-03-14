# Security Policy

## Reporting a Vulnerability

The libthumbor maintainers take security vulnerabilities seriously. If you
discover a security issue in libthumbor, please report it responsibly.

Please **DO NOT open a public GitHub issue** for security vulnerabilities.

Instead, please report the vulnerability privately using GitHub's
**Private Vulnerability Reporting** feature:

- Go to the repository's **Security** tab
- Click **Report a vulnerability**
- Submit the details through the GitHub Security Advisory form

Include as much information as possible to help us reproduce the issue:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- A proof of concept (PoC), if available
- Your environment (libthumbor version, Python version, and how URLs are generated)

We will acknowledge receipt of your report as soon as possible and work with
you to understand and resolve the issue.

## Responsible Disclosure

We ask that you follow responsible disclosure practices:

- Do not publicly disclose the vulnerability before it has been addressed.
- Allow the maintainers reasonable time to investigate and fix the issue.
- Coordinate with us before publishing advisories, blog posts, or CVEs.

Once the issue is fixed, we will publicly acknowledge your contribution unless
you prefer to remain anonymous.

## Supported Versions

Security fixes are typically provided for the most recent stable versions of
libthumbor.

| Version                 | Supported      |
| ----------------------- | -------------- |
| Latest release          | Yes            |
| Previous minor versions | Best effort    |
| Older versions          | No             |

Users are strongly encouraged to keep their libthumbor installations up to
date.

## Security Considerations When Using libthumbor

When using libthumbor in production, please consider the following:

- Protect the signing key used to generate thumbor URLs.
- Rotate keys if you suspect they may have been exposed.
- Avoid embedding secrets in source code, examples, or test fixtures.
- Keep Python and dependency versions up to date.
- Validate integration behavior when changing URL-generation logic.

Because libthumbor is responsible for generating signed image URLs, weak key
management can allow attackers to craft or tamper with image transformation
requests.

## Acknowledgements

We appreciate the efforts of security researchers and the open-source
community in responsibly reporting vulnerabilities and helping improve the
security of libthumbor.
