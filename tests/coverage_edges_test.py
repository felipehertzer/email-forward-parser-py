import re
from collections.abc import Iterator
from email import policy
from email.message import EmailMessage, Message
from email.mime.message import MIMEMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import Parser
from pathlib import Path
from typing import cast
from unittest.mock import patch

from emailforwardparser import forward_parser as fp, loop, regexs, utils
from emailforwardparser.client import EmailParserClient

FORWARDED_WITH_CC = """Hi team

---------- Forwarded message ---------
From: Jane Doe <jane@example.com>
Date: Mon, 1 Jan 2024 at 12:00 PM
Subject: Original subject
To: Bob <bob@example.com>
Cc: Copy <copy@example.com>

Original body.
"""


class WalkMessage:
    def __init__(self, *parts: object) -> None:
        self.parts = parts

    def walk(self) -> Iterator[object]:
        return iter(self.parts)


class AttachmentPart:
    def __init__(
        self,
        content_type: str,
        payload: object = None,
        filename: str | None = None,
        charset: str = "utf-8",
        content: object = None,
        raises: bool = False,
    ) -> None:
        self.content_type = content_type
        self.payload = payload
        self.filename = filename
        self.charset = charset
        self.content = content
        self.raises = raises

    def get_content_type(self) -> str:
        return self.content_type

    def get_payload(self, decode: bool = False) -> object:
        if self.raises:
            raise ValueError("bad payload")
        return self.payload

    def get_content(self) -> object:
        return self.content

    def get_filename(self) -> str | None:
        return self.filename

    def get_content_charset(self) -> str:
        return self.charset


class PayloadPart:
    def __init__(
        self,
        content: object = None,
        decoded: object = None,
        raw: object = None,
        charset: str = "utf-8",
        raises: bool = False,
    ) -> None:
        self.content = content
        self.decoded = decoded
        self.raw = raw
        self.charset = charset
        self.raises = raises

    def get_content(self) -> object:
        if self.raises:
            raise ValueError("decode failed")
        return self.content

    def get_payload(self, decode: bool = False) -> object:
        return self.decoded if decode else self.raw

    def get_content_charset(self) -> str:
        return self.charset


def message_stub(value: object) -> Message:
    return cast(Message, value)


def test_client_file_and_non_forwarded_eml_message_branch(tmp_path: Path) -> None:
    message = EmailMessage()
    message["From"] = "Plain <plain@example.com>"
    message["To"] = "parser@example.com"
    message["Subject"] = "Plain"
    message.set_content("Plain body.")
    path = tmp_path / "plain.eml"
    path.write_text(message.as_string(), encoding="utf8")

    data = EmailParserClient().get_original_eml_from_file(str(path))

    assert data["forward"] is False
    assert data["Send-To"] == "plain@example.com"
    assert "Plain body." in data["eml"]


def test_client_attached_forwarded_message_metadata_branch() -> None:
    attached = EmailMessage()
    attached["From"] = "Forwarder <forwarder@example.com>"
    attached["Subject"] = "Fwd: Original subject"
    attached.set_content(FORWARDED_WITH_CC)

    wrapper = MIMEMultipart()
    wrapper["From"] = "Outer <outer@example.com>"
    wrapper.attach(MIMEText("See attached.", "plain", "utf-8"))
    wrapper.attach(MIMEMessage(attached))

    metadata = EmailParserClient().get_original_metadata(wrapper.as_string())

    assert metadata.forwarded is True
    assert metadata.email.subject == "Original subject"
    assert metadata.email.cc == [fp.MailboxResult("Copy", "copy@example.com")]


def test_client_rebuilds_forwarded_multipart_message_with_cc_and_extra_parts() -> None:
    message = MIMEMultipart()
    message["From"] = "Forwarder <forwarder@example.com>"
    message["Subject"] = "Fwd: Original subject"
    message.attach(MIMEText(FORWARDED_WITH_CC, "plain", "utf-8"))
    message.attach(MIMEText("<p>forwarded html</p>", "html", "utf-8"))

    alternative = MIMEMultipart("alternative")
    alternative.attach(MIMEText("alternative plain", "plain", "utf-8"))
    alternative.attach(MIMEText("<p>alternative html</p>", "html", "utf-8"))
    message.attach(alternative)

    attachment = MIMEText("attachment text", "plain", "utf-8")
    attachment.add_header("Content-Disposition", "attachment", filename="note.txt")
    message.attach(attachment)

    data = EmailParserClient().get_original_eml(message.as_string())
    rebuilt = Parser(policy=policy.default).parsestr(data["eml"])
    decoded_parts = [
        part.get_content()
        for part in rebuilt.walk()
        if not part.is_multipart() and isinstance(part.get_content(), str)
    ]

    assert data["forward"] is True
    assert "copy@example.com" in data["eml"]
    assert any("forwarded html" in part for part in decoded_parts)
    assert 'attachment; filename="note.txt"' in data["eml"]


def test_client_helpers_cover_empty_headers_and_non_text_multipart() -> None:
    client = EmailParserClient()
    html_only = MIMEMultipart()
    html_only.attach(MIMEText("<p>html only</p>", "html", "utf-8"))
    no_subject = EmailMessage()
    no_subject.set_content("not forwarded")

    assert client._get_body(html_only) == ""
    assert client._get_forwarded_metadata(no_subject).forwarded is False
    assert client._first_header_address("") == ""
    assert client._mailboxes_from_header("") == []
    assert client._format_addresses([fp.MailboxResult("Undisclosed", "")]) == "Undisclosed"


def test_client_eml_attachment_fallbacks_and_decoders() -> None:
    client = EmailParserClient()
    attached = EmailMessage()
    attached["Subject"] = "Content branch"
    attached.set_content("content body")

    assert (
        client._get_eml_attachment(
            message_stub(WalkMessage(AttachmentPart("message/rfc822", payload=["raw eml"])))
        )
        == "raw eml"
    )
    assert "Content branch" in client._get_eml_attachment(
        message_stub(WalkMessage(AttachmentPart("message/rfc822", payload=[], content=attached)))
    )
    assert (
        client._get_eml_attachment(
            message_stub(WalkMessage(AttachmentPart("message/rfc822", raises=True)))
        )
        == ""
    )
    assert (
        client._get_eml_attachment(
            message_stub(
                WalkMessage(
                    AttachmentPart(
                        "application/octet-stream",
                        payload=b"Subject: Bytes\n\nBody",
                        filename="saved.EML",
                    )
                )
            )
        )
        == "Subject: Bytes\n\nBody"
    )
    assert (
        client._get_eml_attachment(
            message_stub(
                WalkMessage(
                    AttachmentPart(
                        "application/octet-stream",
                        payload="U3ViamVjdDogU3RyaW5nCgpCb2R5",
                        filename="saved.eml",
                    )
                )
            )
        )
        == "Subject: String\n\nBody"
    )


def test_client_part_text_fallbacks_and_decode_helpers() -> None:
    client = EmailParserClient()

    assert (
        client._get_part_text(message_stub(PayloadPart(content=b"byte content"))) == "byte content"
    )
    assert (
        client._get_part_text(message_stub(PayloadPart(decoded=b"decoded bytes", raises=True)))
        == "decoded bytes"
    )
    assert (
        client._get_part_text(message_stub(PayloadPart(decoded="decoded string", raises=True)))
        == "decoded string"
    )
    assert (
        client._get_part_text(message_stub(PayloadPart(raw="raw payload", raises=True)))
        == "raw payload"
    )
    assert client._get_part_text(message_stub(PayloadPart(raw=object(), raises=True))) == ""
    assert (
        client._get_part_text(message_stub(PayloadPart(content=object(), decoded="typed fallback")))
        == "typed fallback"
    )
    assert client._decode_bytes(b"default charset") == "default charset"
    assert client.get_decoded_str(None) == ""
    assert client.get_decoded_str(b"byte string") == "byte string"
    assert client.get_decoded_str("YmFzZTY0IHRleHQ=") == "base64 text"
    assert client.get_decoded_str("not base64") == "not base64"


def test_client_typed_edge_paths_are_explicit() -> None:
    client = EmailParserClient()

    class MultipartStringPayload:
        def is_multipart(self) -> bool:
            return True

        def get_payload(self) -> str:
            return "malformed multipart payload"

    rebuilt = client._build_original_email(
        fp.OriginalMetadata(),
        message_stub(MultipartStringPayload()),
    )
    assert rebuilt.is_multipart()

    nested = Message()
    nested.set_type("multipart/alternative")
    nested.set_payload("malformed nested payload")
    outer = MIMEMultipart()
    outer.set_payload([nested])
    client._build_original_email(fp.OriginalMetadata(), outer)

    assert client._format_addresses([fp.MailboxResult()]) == ""
    assert client._mailboxes_from_header("<>") == []

    rfc822_without_content = Message()
    rfc822_without_content.set_type("message/rfc822")
    rfc822_without_content.set_payload([])
    assert client._get_eml_attachment(rfc822_without_content) == ""
    assert (
        client._get_eml_attachment(
            message_stub(
                WalkMessage(
                    AttachmentPart("message/rfc822", payload=[], content="not a message"),
                    AttachmentPart("application/octet-stream"),
                    AttachmentPart("application/octet-stream", filename="note.txt"),
                    AttachmentPart(
                        "application/octet-stream",
                        payload=object(),
                        filename="note.eml",
                    ),
                )
            )
        )
        == ""
    )

    legacy_part = Message()
    legacy_part.set_payload("legacy payload")
    assert client._get_part_text(legacy_part) == "legacy payload"


def test_parse_body_forwarded_subject_without_separator_uses_from_fallback() -> None:
    body = """Intro
From: Jane Doe <jane@example.com>
Date: Mon, 1 Jan 2024 at 12:00 PM
Subject: Original subject

Original body.
"""

    result = fp.get_forwarded_metadata(body, "Fwd: Original subject")

    assert result.forwarded is True
    assert result.message == "Intro"
    assert result.email.from_ == fp.MailboxResult("Jane Doe", "jane@example.com")
    assert result.email.body == "Original body."
    assert fp.parse_body("plain body", True) == fp.ParseBodyResult()


def test_original_body_and_header_fallbacks() -> None:
    assert fp.parse_original_body("Subject: Hello\nbody") == "body"
    assert fp.parse_original_body("No headers\nbody") == "No headers\nbody"
    assert fp.parse_original_body("Reply-To: reply@example.com\n\nreply body") == "reply body"
    assert fp.parse_original_subject("prefix Subject: Lax subject") == "Lax subject"
    assert fp.parse_original_subject("No subject") == ""
    assert fp.parse_original_date("No date", "Date: Today") == "Today"
    assert fp.parse_original_date("Subject: s\nSent: Yesterday", "") == "Yesterday"
    assert fp.parse_original_date("prefix Sent: Yesterday", "") == "Yesterday"
    assert fp.parse_original_date("Subject: s", "") == ""


def test_original_sender_recipient_and_cc_fallbacks() -> None:
    separator = 'On Mon, 1 Jan 2024, "Jane Doe" <jane@example.com> wrote:'

    assert fp.parse_original_from(
        "Subject: x", "From: Jane Doe <jane@example.com>"
    ) == fp.MailboxResult("Jane Doe", "jane@example.com")
    assert fp.parse_original_from(
        "From: Jane Doe", "From: Jane Doe <jane@example.com>"
    ) == fp.MailboxResult("Jane Doe", "jane@example.com")
    assert fp.parse_original_from("No from here", separator) == fp.MailboxResult(
        "Jane Doe", "jane@example.com"
    )
    assert fp.parse_original_date("No date", separator) == "Mon, 1 Jan 2024"
    assert fp.parse_original_from(
        "prefix From: Jane Doe <jane@example.com>", ""
    ) == fp.MailboxResult("Jane Doe", "jane@example.com")
    assert fp.parse_original_from("No from", "No from") == fp.MailboxResult()
    assert fp.parse_original_to("Subject: x", "To: Bob <bob@example.com>") == [
        fp.MailboxResult("Bob", "bob@example.com")
    ]
    assert fp.parse_original_to("To: Bob", "To: Bob <bob@example.com>") == [
        fp.MailboxResult("Bob", "bob@example.com")
    ]
    assert fp.parse_original_to(
        "Subject: s\nSent: d\nCc: c@example.com\nTo: Bob <bob@example.com>", ""
    ) == [fp.MailboxResult("Bob", "bob@example.com")]
    assert fp.parse_original_cc("Subject: s\nSent: d\nCc: c@example.com", "") == [
        fp.MailboxResult("", "c@example.com")
    ]


def test_mailbox_and_loop_utility_edges() -> None:
    assert fp.parse_subject("Plain subject") == ""
    assert fp.parse_mailbox(regexs.ORIGINAL_TO, "No recipient") == []
    assert fp.parse_mailbox(regexs.ORIGINAL_TO, "To: not a valid recipient") == [
        fp.MailboxResult("not a valid recipient", "")
    ]
    assert fp.prepare_mailbox("", "not address") == fp.MailboxResult("not address", "")
    assert fp.prepare_mailbox("same@example.com", "same@example.com") == fp.MailboxResult(
        "", "same@example.com"
    )
    assert fp.parse_body("plain body", False) == fp.ParseBodyResult()
    assert fp.get_forwarded_metadata("plain body", "Plain subject").forwarded is False
    assert loop.loop_regexes_replace([re.compile("missing")], "keep") == "keep"
    assert loop.loop_regexes_split([re.compile("a"), re.compile("b")], "xxb aa", False) == [
        "xxb ",
        "a",
        "a",
    ]


def test_utils_regex_helpers_cover_empty_limited_and_duplicate_splits() -> None:
    named = re.compile(r"(?P<name>Jane)")
    missing = re.compile(r"(?P<name>Missing)")
    repeated = re.compile(r"^(a)")

    assert utils.find_named_matches(named, "Jane") == {"name": "Jane"}
    assert utils.find_named_matches(missing, "Jane") == {}
    assert utils.find_all_string_submatch_index(re.compile("a"), "banana", 1) == [[1, 2]]
    assert utils.split_with_regexp(re.compile("z"), "abc") == ["abc"]
    assert utils.split_with_regexp(repeated, "abc") == ["", "a", "bc"]
    assert utils.is_graphic("\n") is True


def test_parser_unusual_empty_match_paths() -> None:
    with patch(
        "emailforwardparser.forward_parser.parse_mailbox",
        return_value=[fp.MailboxResult()],
    ):
        assert fp.parse_original_from("", "") == fp.MailboxResult()

    with patch(
        "emailforwardparser.forward_parser.loop.loop_regexes_match",
        return_value=(["To:", ""], None),
    ):
        assert fp.parse_mailbox(regexs.ORIGINAL_TO, "To:") == []
