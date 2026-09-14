from emailforwardparser import forward_parser as fp, regexs, utils

GMAIL_FORWARD = """Hi team

---------- Forwarded message ---------
From: Jane Doe <jane@example.com>
Date: Mon, 1 Jan 2024 at 12:00 PM
Subject: Original subject
To: Alice <alice@example.com>; Bob <bob@example.com>
Cc: Charlie <charlie@example.com>; Dana <dana@example.com>

Original body.
"""


def test_parse_gmail_forwarded_body_with_semicolon_recipients() -> None:
    result = fp.get_forwarded_metadata(GMAIL_FORWARD, "Fwd: Original subject")

    assert result.forwarded is True
    assert result.message == "Hi team"
    assert result.email.subject == "Original subject"
    assert result.email.date == "Mon, 1 Jan 2024 at 12:00 PM"
    assert result.email.body == "Original body."
    assert result.email.from_ == fp.MailboxResult("Jane Doe", "jane@example.com")
    assert result.email.to == [
        fp.MailboxResult("Alice", "alice@example.com"),
        fp.MailboxResult("Bob", "bob@example.com"),
    ]
    assert result.email.cc == [
        fp.MailboxResult("Charlie", "charlie@example.com"),
        fp.MailboxResult("Dana", "dana@example.com"),
    ]


def test_parse_gmail_forwarded_body_with_wrapped_from_line() -> None:
    # Gmail wraps a long "From:" line after the "<", putting the address on its own line.
    body = """FYI

---------- Forwarded message ---------
From: Some Very Long Display Name <
some.very.long.address@privaterelay.example.com>
Date: Sun, 13 Sept 2026 at 11:34
Subject: Original subject
To: <me@example.com>

Original body.
"""
    result = fp.get_forwarded_metadata(body, "Fwd: Original subject")

    assert result.forwarded is True
    assert result.email.from_ == fp.MailboxResult(
        "Some Very Long Display Name", "some.very.long.address@privaterelay.example.com"
    )
    assert result.email.subject == "Original subject"
    assert result.email.body == "Original body."


def test_parse_apple_forwarded_body_without_subject() -> None:
    body = """Personal note

Begin forwarded message:

From: Jane Doe <jane@example.com>
Date: Mon, 1 Jan 2024 at 12:00 PM
Subject: Original subject
To: Bob <bob@example.com>

Original body.
"""

    result = fp.get_forwarded_metadata(body)

    assert result.forwarded is True
    assert result.message == "Personal note"
    assert result.email.subject == "Original subject"
    assert result.email.from_ == fp.MailboxResult("Jane Doe", "jane@example.com")
    assert result.email.to == [fp.MailboxResult("Bob", "bob@example.com")]
    assert result.email.body == "Original body."


def test_encoded_forwarded_subject_is_decoded() -> None:
    result = fp.get_forwarded_metadata(
        GMAIL_FORWARD,
        "=?UTF-8?Q?Fwd:_Original_subject?=",
    )

    assert result.forwarded is True
    assert result.email.subject == "Original subject"


def test_parse_mailbox_strips_semicolon_separators_from_bare_addresses() -> None:
    result = fp.parse_mailbox(
        regexs.ORIGINAL_TO,
        "To: alice@example.com; bob@example.com",
    )

    assert result == [
        fp.MailboxResult("", "alice@example.com"),
        fp.MailboxResult("", "bob@example.com"),
    ]


def test_preprocess_removes_control_characters_but_preserves_line_breaks() -> None:
    assert utils.preprocess_string("Fwd:\x00 Hello\nNext") == "Fwd: Hello\nNext"
