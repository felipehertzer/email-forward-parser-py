"""Regression tests for parser crashes, mis-parses and super-linear regexes."""

import base64
import re
import time
from collections.abc import Callable
from functools import partial

from emailforwardparser import forward_parser as fp, loop, regexs, utils
from emailforwardparser.client import EmailParserClient
from emailforwardparser.forward_parser import MailboxResult

GMAIL_SEPARATOR = "---------- Forwarded message ---------"


def elapsed(parse: Callable[[], object]) -> float:
    start = time.perf_counter()
    parse()
    return time.perf_counter() - start


def raw_email(
    subject: str | None, body: str, content_type: str = "text/plain; charset=utf-8"
) -> str:
    encoded = base64.b64encode(body.encode()).decode()
    return (
        "From: Forwarder <forwarder@example.com>\n"
        "To: parser@example.com\n"
        + (f"Subject: {subject}\n" if subject is not None else "")
        + "MIME-Version: 1.0\n"
        + f"Content-Type: {content_type}\n"
        + "Content-Transfer-Encoding: base64\n\n"
        + f"{encoded}\n"
    )


def test_forwarded_body_ending_on_from_line_does_not_crash() -> None:
    result = fp.get_forwarded_metadata("note\nFrom: Jane <jane@example.com>", "Fwd: x")

    assert result.forwarded is True
    assert result.message == "note"
    assert result.email.from_ == MailboxResult("Jane", "jane@example.com")


def test_encoded_words_in_body_keep_line_structure() -> None:
    body = (
        f"Hi\n\n{GMAIL_SEPARATOR}\n"
        "From: =?utf-8?q?J=C3=B6rg?= <jorg@example.com>\n"
        "Subject: Hello\n"
        "To: bob@example.com\n\n"
        "Line one.\nLine two."
    )

    result = fp.get_forwarded_metadata(body)

    assert result.forwarded is True
    assert result.message == "Hi"
    assert result.email.from_ == MailboxResult("Jörg", "jorg@example.com")
    assert result.email.body == "Line one.\nLine two."


def test_undecodable_encoded_words_are_kept_verbatim() -> None:
    assert utils.preprocess_string("a =?x-unknown?q?b?= c") == "a =?x-unknown?q?b?= c"
    assert utils.preprocess_string("=?utf-8?q?=FF?=") == "\N{REPLACEMENT CHARACTER}"
    assert utils.preprocess_string("=?utf-8?q?a?= \t=?utf-8?q?b?=") == "ab"

    raw = raw_email("Fwd: hi", "body =?x-unknown?q?a?= here")
    assert EmailParserClient().get_original_metadata(raw).forwarded is True


def test_unknown_part_charset_falls_back_to_utf8() -> None:
    raw = raw_email(
        "Fwd: hi",
        f"note\n\n{GMAIL_SEPARATOR}\nFrom: Jane <jane@example.com>\nSubject: s\n\ncafé",
        content_type='text/plain; charset="unknown-8bit"',
    )
    client = EmailParserClient()

    result = client.get_original_metadata(raw)

    assert result.forwarded is True
    assert result.email.body == "café"
    assert client.get_original_eml(raw)["forward"] is True
    assert client._decode_bytes(b"x", "idna") == "x"
    assert client.get_decoded_str("YQ==", "no-such-charset") == "a"


def test_line_breaks_inside_parsed_values_never_reach_rebuilt_headers() -> None:
    body = (
        f"hi\n\n{GMAIL_SEPARATOR}\nFrom: Jane <jane@example.com>\n"
        "Date: Mon\rBcc: evil@example.com\nSubject: s\u2028more\nTo: bob@example.com\n\nbody\n"
    )
    raw = raw_email(None, body)
    client = EmailParserClient()

    metadata = client.get_original_metadata(raw)
    assert metadata.email.date == "Mon"
    assert metadata.email.subject == "s\u2028more"
    eml = client.get_original_eml(raw)["eml"]
    assert "Bcc" not in eml
    assert "Subject: s more\n" in eml


def test_byte_order_mark_pattern_does_not_eat_thorn_ff() -> None:
    thorn_ff = "3\N{LATIN SMALL LETTER THORN}FF"
    body = f"{GMAIL_SEPARATOR}\nFrom: Jane <jane@example.com>\nSubject: s\n\nSize: {thorn_ff}."

    assert fp.get_forwarded_metadata(body).email.body == f"Size: {thorn_ff}."
    assert regexs.BYTE_ORDER_MARK.sub("", "a\N{ZERO WIDTH NO-BREAK SPACE}b") == "ab"


def test_romanian_and_ukrainian_from_labels_match_without_space() -> None:
    romanian = f"{GMAIL_SEPARATOR}\nDe la: jane@example.com\nSubiectul: s\n\nbody"
    # Apple Mail (uk) "Від кого:" and "Тема:", with the Cyrillic letters that look Latin
    # spelled by name.
    from_label = (
        "\N{CYRILLIC CAPITAL LETTER VE}\N{CYRILLIC SMALL LETTER BYELORUSSIAN-UKRAINIAN I}д кого"
    )
    subject_label = (
        "\N{CYRILLIC CAPITAL LETTER TE}\N{CYRILLIC SMALL LETTER IE}м\N{CYRILLIC SMALL LETTER A}"
    )
    ukrainian = (
        "Початок листа, що пересилається:\n\n"
        f"{from_label}: jane@example.com\n{subject_label}: s\n\nbody"
    )

    for body in (romanian, ukrainian):
        assert fp.get_forwarded_metadata(body).email.from_ == MailboxResult("", "jane@example.com")


def test_lax_polish_cc_label_requires_colon() -> None:
    body = (
        "----- Forwarded Message ----- From: Jane <jane@example.com> "
        "To: Bob <bob@example.com> Sent: Mon Subject: Hi\n\nDwight says hi"
    )

    assert fp.get_forwarded_metadata(body, "Fwd: Hi").email.cc == []


def test_quote_marker_and_blank_lines_before_separator_stay_out_of_message() -> None:
    body = (
        "note\n>\n\nBegin forwarded message:\n\n"
        "From: Jane <jane@example.com>\nSubject: s\nTo: bob@example.com\n\nbody"
    )

    assert fp.get_forwarded_metadata(body).message == "note"


def test_blank_lines_between_repeated_headers_are_not_the_body() -> None:
    text = (
        "From: a@example.com\nCc: a@example.com\n\n\nCc: b@example.com\nTo: c@example.com\n\nBody"
    )

    assert fp.parse_original_body(text) == "Body"


def test_mailbox_address_keeps_optional_dot_semantics() -> None:
    assert fp.prepare_mailbox("", "user@localhost") == MailboxResult("", "user@localhost")
    assert fp.prepare_mailbox("", "a@b") == MailboxResult("a@b", "")


def test_blank_line_runs_parse_in_linear_time() -> None:
    header = f"{GMAIL_SEPARATOR}\nFrom: Jane <jane@example.com>\nSubject: s\nTo: b@example.com\n\n"

    assert elapsed(lambda: fp.get_forwarded_metadata("Hi\n" + "\n" * 20_000 + "x")) < 1
    assert elapsed(lambda: fp.get_forwarded_metadata(header + "a\n" + "\n" * 20_000 + "x")) < 1


def test_long_recipient_lines_parse_quickly() -> None:
    named = "A <a@example.com>, " * 600
    mailto = "<mailto:" * 800
    spaces = "x" + " " * 20_000 + "y"

    for line in (named, mailto, spaces):
        body = f"{GMAIL_SEPARATOR}\nFrom: a@example.com\nTo: {line}\n\nbody"
        assert elapsed(partial(fp.get_forwarded_metadata, body)) < 1

    long_token = "a@" + "b" * 30_000 + " x"
    assert elapsed(lambda: fp.prepare_mailbox("", long_token)) < 1


def test_lax_patterns_scan_whitespace_runs_once() -> None:
    text = "From: a" + " " * 20_000 + "\nSent:" + " " * 20_000 + "x"

    assert elapsed(lambda: loop.loop_regexes_match(regexs.ORIGINAL_FROM_LAX, text)) < 1
    assert elapsed(lambda: loop.loop_regexes_replace(regexs.ORIGINAL_DATE_LAX, text)) < 1
    assert loop.loop_regexes_replace(regexs.ORIGINAL_DATE_LAX, "To: a Sent: b") == "To: a"


def test_loop_regexes_match_keeps_earliest_then_first_listed() -> None:
    later, earlier, tie = re.compile("c"), re.compile("b"), re.compile("bc")

    assert loop.loop_regexes_match([earlier, later], "abc") == (["b"], earlier)
    assert loop.loop_regexes_match([later, earlier], "abc") == (["b"], earlier)
    assert loop.loop_regexes_match([earlier, tie], "bc") == (["b"], earlier)
