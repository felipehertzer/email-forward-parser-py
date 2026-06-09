# email-forward-parser-py

`email-forward-parser` extracts the original message details from forwarded email
content. It can work with plain forwarded bodies or full `.eml` messages, including
common MIME encodings and attached `.eml` files.

The package is useful when you receive emails forwarded by users or mailboxes and
need to recover the original sender, recipients, subject, sent date, and body.

## Features

- Detects forwarded messages from subject prefixes such as `Fwd:` and `FW:`.
- Parses forwarded bodies from Gmail, Apple Mail, Outlook/Office 365, Thunderbird,
  Yahoo Mail, HubSpot, Missive, IONOS, and several localized clients.
- Extracts original metadata: `From`, `To`, `Cc`, `Subject`, `Date`, and body.
- Parses full `.eml` messages with MIME decoding.
- Handles quoted-printable/base64 text bodies and attached `message/rfc822` or
  `.eml` attachments.
- Rebuilds an `.eml` string for the original message when a forwarded email is
  detected.
- Ships with a 100% statement coverage gate.

## Installation

```bash
python -m pip install email-forward-parser
```

Python 3.10 or newer is required.

The distribution name is `email-forward-parser`, but the import package is
`emailforwardparser`:

```python
from emailforwardparser.forward_parser import get_forwarded_metadata
from emailforwardparser.client import EmailParserClient
```

## Quick Start

Use `get_forwarded_metadata()` when you already have the email body text.

```python
from emailforwardparser.forward_parser import get_forwarded_metadata

body = """Hi team

---------- Forwarded message ---------
From: Jane Doe <jane@example.com>
Date: Mon, 1 Jan 2024 at 12:00 PM
Subject: Original subject
To: Bob <bob@example.com>
Cc: Copy <copy@example.com>

Original body.
"""

result = get_forwarded_metadata(body, "Fwd: Original subject")

print(result.forwarded)             # True
print(result.message)               # Hi team
print(result.email.subject)         # Original subject
print(result.email.from_.name)      # Jane Doe
print(result.email.from_.address)   # jane@example.com
print(result.email.to[0].address)   # bob@example.com
print(result.email.cc[0].address)   # copy@example.com
print(result.email.body)            # Original body.
```

Use `EmailParserClient` when you have a full `.eml` message.

```python
from emailforwardparser.client import EmailParserClient

client = EmailParserClient()

with open("forwarded.eml", encoding="utf8") as file:
    raw_eml = file.read()

metadata = client.get_original_metadata(raw_eml)

if metadata.forwarded:
    print(metadata.email.from_.address)
    print(metadata.email.subject)
    print(metadata.email.body)
```

## API

### `get_forwarded_metadata(body, subject=None)`

Parses a forwarded body string and returns a `ForwardMetadata` dataclass.

```python
from emailforwardparser.forward_parser import get_forwarded_metadata

result = get_forwarded_metadata(body, subject)
```

`subject` is optional. Passing it helps the parser detect forwards that have a
forwarded subject prefix but no separator line in the body.

### `ForwardMetadata`

```python
@dataclass
class ForwardMetadata:
    forwarded: bool
    message: str
    email: OriginalMetadata
```

- `forwarded`: `True` when forwarded content was detected.
- `message`: the note written by the person who forwarded the email, before the
  forwarded block.
- `email`: metadata extracted from the original email.

### `OriginalMetadata`

```python
@dataclass
class OriginalMetadata:
    date: str
    subject: str
    body: str
    from_: MailboxResult
    to: list[MailboxResult]
    cc: list[MailboxResult]
```

The sender field is named `from_` because `from` is a Python keyword.

### `MailboxResult`

```python
@dataclass
class MailboxResult:
    name: str
    address: str
```

When a mailbox line has no valid email address, `address` is empty and the raw
value is kept in `name`.

### `EmailParserClient`

`EmailParserClient` is the high-level wrapper for full `.eml` messages.

```python
from emailforwardparser.client import EmailParserClient

client = EmailParserClient()
```

Methods:

- `get_original_metadata(email: str) -> ForwardMetadata`
  Parses a raw `.eml` string and returns metadata for the original email. If the
  message is not forwarded, it returns metadata for the message itself.
- `get_original_metadata_from_file(file_path: str) -> ForwardMetadata`
  Reads a `.eml` file and returns the same metadata object.
- `get_original_eml(email: str) -> dict`
  Returns a dictionary with:
  - `forward`: whether the input was detected as forwarded.
  - `Send-To`: the first address from the wrapper message's `From` header.
  - `eml`: a raw `.eml` string for the original message when forwarded, or the
    input/attached message when not forwarded.
- `get_original_eml_from_file(file_path: str) -> dict`
  Reads a `.eml` file and returns the same dictionary.

## Examples

### Parse an Apple Mail Forward Without a Subject

```python
from emailforwardparser.forward_parser import get_forwarded_metadata

body = """Personal note

Begin forwarded message:

From: Jane Doe <jane@example.com>
Date: Mon, 1 Jan 2024 at 12:00 PM
Subject: Original subject
To: Bob <bob@example.com>

Original body.
"""

result = get_forwarded_metadata(body)

assert result.forwarded is True
assert result.message == "Personal note"
assert result.email.subject == "Original subject"
assert result.email.from_.address == "jane@example.com"
```

### Parse a Quoted-Printable `.eml`

```python
from emailforwardparser.client import EmailParserClient

raw_eml = """From: Forwarder <forwarder@example.com>
To: parser@example.com
Subject: Fwd: Original subject
MIME-Version: 1.0
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: quoted-printable

Hi=0A=0A---------- Forwarded message ---------=0AFrom: Jane Doe <jane@example.com>=
=0ADate: Mon, 1 Jan 2024 at 12:00 PM=0ASubject: Original subject=0ATo: Bob =
<bob@example.com>=0A=0AOriginal caf=C3=A9 body.=0A
"""

metadata = EmailParserClient().get_original_metadata(raw_eml)

assert metadata.forwarded is True
assert metadata.email.body == "Original café body."
```

### Rebuild the Original `.eml`

```python
from email.message import EmailMessage

from emailforwardparser.client import EmailParserClient

message = EmailMessage()
message["From"] = "Forwarder <forwarder@example.com>"
message["To"] = "parser@example.com"
message["Subject"] = "Fwd: Original subject"
message.set_content("""Hi

---------- Forwarded message ---------
From: Jane Doe <jane@example.com>
Date: Mon, 1 Jan 2024 at 12:00 PM
Subject: Original subject
To: Bob <bob@example.com>

Original body.
""")

data = EmailParserClient().get_original_eml(message.as_string())

assert data["forward"] is True
print(data["eml"])
```

### Read From a File

```python
from emailforwardparser.client import EmailParserClient

client = EmailParserClient()

metadata = client.get_original_metadata_from_file("forwarded.eml")
data = client.get_original_eml_from_file("forwarded.eml")

print(metadata.email.subject)
print(data["eml"])
```

### Non-Forwarded Messages

If a message is not forwarded, `forwarded` is `False`. With the client wrapper,
the returned `email` metadata describes the message itself.

```python
from emailforwardparser.client import EmailParserClient

metadata = EmailParserClient().get_original_metadata(raw_eml)

if not metadata.forwarded:
    print("This was not a forwarded message")
    print(metadata.email.subject)
```

## Behavior Notes

- Parsing is regex-based. It is designed for common forwarded-message formats,
  not every possible custom email template.
- Missing fields are returned as empty strings or empty lists.
- Multiple `To` and `Cc` recipients are returned in order.
- The parser normalizes common email encodings and non-breaking spaces.
- The client prefers the first non-attachment `text/plain` body part when reading
  multipart `.eml` messages.
- Attached `.eml` messages are returned directly when present.

## Development

Install the development and test tools:

```bash
python -m pip install -e ".[dev,test]"
```

Run the full local quality gate:

```bash
python -m isort --check-only emailforwardparser tests
python -m black --check emailforwardparser tests
python -m ruff check emailforwardparser tests
python -m mypy
python -m pytest
```

`pytest` is configured to require 100% statement coverage.

## Release

Build and verify the distribution:

```bash
python -m pip install --upgrade build twine
python -m pytest
rm -rf dist build
python -m build
python -m twine check dist/*
```

Upload to PyPI:

```bash
python -m twine upload dist/*
```

## License and Credits

This project is distributed under the Apache License, Version 2.0. See
[`LICENSE`](LICENSE) for the full license text.

The project was originally created by Garrett Marking. This fork/package includes
additional maintenance, packaging, typing, test coverage, and parser/client fixes
by Felipe Hertzer.

Apache 2.0 allows redistribution and modification, including publishing to PyPI,
as long as the license conditions are followed. In practice for this package:

- Keep the Apache 2.0 license text with redistributions.
- Keep existing attribution notices from the source distribution.
- Keep the `NOTICE` file with source and binary distributions.
- Make it clear when files have been modified.

For the canonical license terms, refer to the Apache Software Foundation's
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) page.
