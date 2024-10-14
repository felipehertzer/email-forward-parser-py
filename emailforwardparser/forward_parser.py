from dataclasses import dataclass, field
from re import Pattern

from emailforwardparser import loop, regexs, utils


@dataclass
class MailboxResult:
    """Class storing the name and address of a mailbox."""
    name: str = ""
    address: str = ""


@dataclass
class ParseBodyResult:
    """Class storing metadata of parsed forwarded email."""
    body: str = ""
    message: str = ""
    email: str = ""


@dataclass
class OriginalMetadata:
    """Class storing metadata of original content in forwarded message."""
    date: str = ""
    subject: str = ""
    body: str = ""
    from_: MailboxResult = field(default_factory=MailboxResult)
    to: list[MailboxResult] = field(default_factory=list)
    cc: list[MailboxResult] = field(default_factory=list)


@dataclass
class ForwardMetadata:
    """Result object storing forwarded email metadata."""
    forwarded: bool = False
    message: str = ""
    email: OriginalMetadata = field(default_factory=OriginalMetadata)


def parse_subject(subject: str) -> str:
    match, _ = loop.loop_regexes_match(regexs.SUBJECT, subject)
    if len(match) > 0:
        return match[1].strip()
    return ""


def parse_body(body: str, forwarded: bool) -> ParseBodyResult:
    body = regexs.CARRIAGE_RETURN.sub("\n", body)
    body = regexs.BYTE_ORDER_MARK.sub("", body)
    body = regexs.TRAILING_NON_BREAKING_SPACE.sub("", body)
    body = regexs.NON_BREAKING_SPACE.sub(" ", body)
    match = loop.loop_regexes_split(regexs.SEPARATOR, body, True)
    # match[0]: message before fwd spearator
    # match[1]: seperator
    # match[2]: message after seperator
    if len(match) > 2:
        email = match[-1]
        return ParseBodyResult(
            body=body,
            message=match[0].strip(),
            email=email.strip()
        )

    if forwarded:
        match = loop.loop_regexes_split(
            regexs.ORIGINAL_FROM, body, True)
        if len(match) > 2:
            email = "".join(match[i] for i in [1, 3])
            return ParseBodyResult(
                body=body, message=match[0].strip(), email=email.strip()
            )
    return ParseBodyResult()


def parse_original_body(text: str) -> str:
    regexes = [regexs.ORIGINAL_SUBJECT, regexs.ORIGINAL_CC,
               regexs.ORIGINAL_TO, regexs.ORIGINAL_REPLY_TO]

    for regex in regexes:
        match = loop.loop_regexes_split(regex, text, True)
        if len(match) > 3 and match[3].startswith("\n\n"):
            body = match[3]
            return body.strip()
    match = loop.loop_regexes_split(
        regexs.ORIGINAL_SUBJECT + regexs.ORIGINAL_SUBJECT_LAX, text, True)
    if len(match) > 3:
        body = match[3]
        return body.strip()
    return text.strip()


def parse_original_email(text: str, body: str) -> OriginalMetadata:
    text = regexs.BYTE_ORDER_MARK.sub("", text)
    text = regexs.QUOTE_LINE_BREAK_OPTIONAL.sub("", text)
    text = regexs.QUOTE_LINE_BREAK.sub("", text)
    text = regexs.QUOTE.sub("", text)
    text = regexs.FOUR_SPACES.sub("", text)

    return OriginalMetadata(
        body=parse_original_body(text),
        from_=parse_original_from(text, body),
        to=parse_original_to(text, body),
        cc=parse_original_cc(text, body),
        subject=parse_original_subject(text),
        date=parse_original_date(text, body),
    )


def parse_original_from(text: str, body: str) -> MailboxResult:
    authors = parse_mailbox(regexs.ORIGINAL_FROM, text) or parse_mailbox(regexs.ORIGINAL_FROM, body)
    if authors:
        author = authors[0]
        if author.name or author.address:
            return author

    match, pattern = loop.loop_regexes_match(
        regexs.SEPARATOR_WITH_INFORMATION, body)
    if len(match) == 4:
        named_matches = utils.find_named_matches(pattern, body)
        return prepare_mailbox(
            named_matches.get("from_name", ""), named_matches.get(
                "from_address", "")
        )

    match, _ = loop.loop_regexes_match(regexs.ORIGINAL_FROM_LAX, text)
    if len(match) > 1:
        name = match[2]
        address = match[3]
        return prepare_mailbox(name, address)
    return MailboxResult()


def parse_original_to(text: str, body) -> list[MailboxResult]:
    recipients = parse_mailbox(regexs.ORIGINAL_TO, text) or parse_mailbox(regexs.ORIGINAL_TO, body)
    if recipients:
        return recipients

    text = loop.loop_regexes_replace(regexs.ORIGINAL_SUBJECT_LAX, text)
    text = loop.loop_regexes_replace(regexs.ORIGINAL_DATE_LAX, text)
    text = loop.loop_regexes_replace(regexs.ORIGINAL_CC_LAX, text)
    return parse_mailbox(regexs.ORIGINAL_TO_LAX, text)


def parse_original_cc(text: str, body: str) -> list[MailboxResult]:
    recipients = parse_mailbox(regexs.ORIGINAL_CC, text) or parse_mailbox(regexs.ORIGINAL_CC, body)
    if recipients:
        return recipients

    text = loop.loop_regexes_replace(regexs.ORIGINAL_SUBJECT_LAX, text)
    text = loop.loop_regexes_replace(regexs.ORIGINAL_DATE_LAX, text)
    return parse_mailbox(regexs.ORIGINAL_CC_LAX, text)


def parse_original_subject(text: str) -> str:
    match, _ = loop.loop_regexes_match(regexs.ORIGINAL_SUBJECT, text)
    if match:
        return match[1].strip()
    match, _ = loop.loop_regexes_match(regexs.ORIGINAL_SUBJECT_LAX, text)
    if match:
        return match[1].strip()
    return ""


def parse_original_date(text: str, body: str) -> str:
    match = loop.loop_regexes_match(regexs.ORIGINAL_DATE, text)[0] or loop.loop_regexes_match(regexs.ORIGINAL_DATE, body)[0]
    if match:
        return match[1].strip()
    match, pattern = loop.loop_regexes_match(
        regexs.SEPARATOR_WITH_INFORMATION, body)

    if len(match) == 4:
        named_matches = utils.find_named_matches(pattern, body)
        return named_matches.get("date", "").strip()

    text = loop.loop_regexes_replace(regexs.ORIGINAL_SUBJECT_LAX, text)
    match, _ = loop.loop_regexes_match(regexs.ORIGINAL_DATE_LAX, text)
    if match:
        return match[1].strip()
    return ""


def parse_mailbox(regexes: list[Pattern], text: str) -> list[MailboxResult]:
    match, _ = loop.loop_regexes_match(regexes, text)
    if match:
        mailboxes_line = match[-1].strip()
        if mailboxes_line:
            mailboxes = []
            while mailboxes_line:
                mailbox_match, _ = loop.loop_regexes_match(
                    regexs.MAILBOX, mailboxes_line)
                if mailbox_match:
                    if len(mailbox_match) == 3:
                        name = mailbox_match[1]
                        address = mailbox_match[2]
                    else:
                        name = ""
                        address = mailbox_match[1]
                    mailboxes.append(prepare_mailbox(name, address))
                    mailboxes_line = mailboxes_line.replace(
                        mailbox_match[0], "", 1
                    ).strip()
                    if mailboxes_line and mailboxes_line[0] in regexs.MAILBOX_SEPARATORS:
                        mailboxes_line = mailboxes_line[1:].strip()
                else:
                    mailboxes.append(prepare_mailbox("", mailboxes_line))
                    mailboxes_line = ""
            return mailboxes
    return []


def prepare_mailbox(name: str, address: str) -> MailboxResult:
    name = name.strip()
    address = address.strip()

    match, _ = loop.loop_regexes_match(regexs.MAILBOX_ADDRESS, address)
    if not match:
        name = address
        address = ""
    if address == name:
        name = ""
    return MailboxResult(name.strip(), address.strip())


def get_forwarded_metadata(body: str, subject: str | None = None) -> ForwardMetadata:
    email = OriginalMetadata()
    forwarded = False
    body_result = ParseBodyResult()
    parsed_subject = ""

    if subject:
        subject = utils.preprocess_string(subject)
        parsed_subject = parse_subject(subject)
        if parsed_subject:
            forwarded = True

    if not subject or forwarded:
        body = utils.preprocess_string(body)
        body_result = parse_body(body, forwarded)
        if body_result.email:
            forwarded = True
            email = parse_original_email(body_result.email, body_result.body)
    subject_result = parsed_subject if parsed_subject else email.subject

    return ForwardMetadata(
        forwarded=forwarded,
        message=body_result.message,
        email=OriginalMetadata(
            date=email.date,
            subject=subject_result,
            body=email.body,
            from_=email.from_,
            to=email.to,
            cc=email.cc,
        ),
    )
