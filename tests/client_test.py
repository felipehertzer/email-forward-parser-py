from email import policy
from email.message import EmailMessage
from email.mime.message import MIMEMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import Parser

from emailforwardparser.client import EmailParserClient
from emailforwardparser.forward_parser import MailboxResult

FORWARDED_TEXT = """Hi team

---------- Forwarded message ---------
From: Jane Doe <jane@example.com>
Date: Mon, 1 Jan 2024 at 12:00 PM
Subject: Original subject
To: Bob <bob@example.com>

Original body.
"""


def parse_message(raw: str) -> EmailMessage:
    return Parser(policy=policy.default).parsestr(raw)


def test_get_original_eml_rebuilds_forwarded_plain_text_message():
    message = EmailMessage()
    message["From"] = "Forwarder <forwarder@example.com>"
    message["To"] = "parser@example.com"
    message["Subject"] = "Fwd: Original subject"
    message.set_content(FORWARDED_TEXT)

    data = EmailParserClient().get_original_eml(message.as_string())
    original = parse_message(data["eml"])

    assert data["forward"] is True
    assert data["Send-To"] == "forwarder@example.com"
    assert str(original["Subject"]) == "Original subject"
    assert str(original["From"]) == "Jane Doe <jane@example.com>"
    assert str(original["To"]) == "Bob <bob@example.com>"
    assert original.get_content().strip() == "Original body."


def test_get_original_metadata_decodes_quoted_printable_plain_text():
    raw = """From: Forwarder <forwarder@example.com>
To: parser@example.com
Subject: Fwd: Original subject
MIME-Version: 1.0
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: quoted-printable

Hi=0A=0A---------- Forwarded message ---------=0AFrom: Jane Doe <jane@example.c=
om>=0ADate: Mon, 1 Jan 2024 at 12:00 PM=0ASubject: Original subject=0ATo: Bob=
 <bob@example.com>=0A=0AOriginal caf=C3=A9 body.=0A
"""

    result = EmailParserClient().get_original_metadata(raw)

    assert result.forwarded is True
    assert result.email.body == "Original caf\u00e9 body."
    assert result.email.from_ == MailboxResult("Jane Doe", "jane@example.com")


def test_get_original_metadata_from_file_uses_same_parser_path(tmp_path):
    message = EmailMessage()
    message["From"] = "Forwarder <forwarder@example.com>"
    message["To"] = "parser@example.com"
    message["Subject"] = "Fwd: Original subject"
    message.set_content(FORWARDED_TEXT)
    file_path = tmp_path / "forwarded.eml"
    file_path.write_text(message.as_string(), encoding="utf8")

    result = EmailParserClient().get_original_metadata_from_file(str(file_path))

    assert result.forwarded is True
    assert result.email.subject == "Original subject"
    assert result.email.body == "Original body."


def test_get_original_metadata_for_non_forwarded_message_uses_message_headers():
    message = EmailMessage()
    message["From"] = "Jane Doe <jane@example.com>"
    message["To"] = "Bob <bob@example.com>"
    message["Cc"] = "Copy <copy@example.com>"
    message["Subject"] = "Plain subject"
    message["Date"] = "Mon, 01 Jan 2024 12:00:00 +0000"
    message.set_content("Plain body.")

    result = EmailParserClient().get_original_metadata(message.as_string())

    assert result.forwarded is False
    assert result.email.subject == "Plain subject"
    assert result.email.date == "Mon, 01 Jan 2024 12:00:00 +0000"
    assert result.email.body == "Plain body."
    assert result.email.from_ == MailboxResult("Jane Doe", "jane@example.com")
    assert result.email.to == [MailboxResult("Bob", "bob@example.com")]
    assert result.email.cc == [MailboxResult("Copy", "copy@example.com")]


def test_get_original_eml_returns_attached_message_when_present():
    attached = EmailMessage()
    attached["From"] = "Jane Doe <jane@example.com>"
    attached["To"] = "Bob <bob@example.com>"
    attached["Subject"] = "Attached subject"
    attached["Date"] = "Mon, 01 Jan 2024 12:00:00 +0000"
    attached.set_content("Attached body.")

    wrapper = MIMEMultipart()
    wrapper["From"] = "Forwarder <forwarder@example.com>"
    wrapper["To"] = "parser@example.com"
    wrapper["Subject"] = "See attached"
    wrapper.attach(MIMEText("Please see the attached email.", "plain", "utf-8"))
    wrapper.attach(MIMEMessage(attached))

    data = EmailParserClient().get_original_eml(wrapper.as_string())
    metadata = EmailParserClient().get_original_metadata(wrapper.as_string())

    assert data["forward"] is False
    assert data["Send-To"] == "forwarder@example.com"
    assert "Subject: Attached subject" in data["eml"]
    assert metadata.forwarded is False
    assert metadata.email.subject == "Attached subject"
    assert metadata.email.body == "Attached body."
    assert metadata.email.from_ == MailboxResult("Jane Doe", "jane@example.com")
