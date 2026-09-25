from __future__ import annotations

import base64
import binascii
from email import policy
from email.message import EmailMessage, Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import Parser
from email.utils import formataddr, getaddresses
from typing import TypedDict, cast

import structlog
from structlog.stdlib import BoundLogger

from emailforwardparser import forward_parser as fp

ParsedEmail = TypedDict(
    "ParsedEmail",
    {"forward": bool, "eml": str, "Send-To": str},
)

LOGGER = cast(BoundLogger, structlog.get_logger(__name__))


class EmailParserClient:
    """
    A client for parsing email messages, with support for detecting and handling forwarded emails.
    """

    def get_original_eml(self, email: str) -> ParsedEmail:
        """
        Retrieve the original email message as a dict, including metadata and content.

        If any field contains invalid data, the empty string will replace it.

        :param email: Contents of email to be parsed.
        :type email: str
        :return: A dictionary containing the email metadata and content.
        :rtype: dict
        """
        msg = self._parse_message(email)
        send_to = self._first_header_address(msg.get("From", ""))
        eml = self._get_eml_attachment(msg)
        if eml:
            return self._get_dict(eml, fp.OriginalMetadata(), False, send_to=send_to)
        original_metadata = self._get_forwarded_metadata(msg)
        return self._get_dict(
            msg, original_metadata.email, original_metadata.forwarded, send_to=send_to
        )

    def get_original_eml_from_file(self, file_path: str) -> ParsedEmail:
        """
        Retrieve the original email message, including metadata and content.

        :param file_path: The path to the email file to parse.
        :type file_path: str
        :return: A dictionary containing the original receiver and eml content.
        :rtype: dict
        """
        return self.get_original_eml(self._get_file_content(file_path))

    def get_original_metadata(self, email: str) -> fp.ForwardMetadata:
        """
        Extract metadata from the original or forwarded email.

        :param email: Contents of email to be parsed.
        :type email: str
        :return: An object containing metadata of the original email.
        :rtype: fp.ForwardMetadata
        """
        msg = self._parse_message(email)
        original_metadata = self._get_forwarded_metadata(msg)
        if original_metadata.forwarded:
            return original_metadata

        eml = self._get_eml_attachment(msg)
        if eml:
            attached_message = self._parse_message(eml)
            attached_metadata = self._get_forwarded_metadata(attached_message)
            if attached_metadata.forwarded:
                return attached_metadata
            return fp.ForwardMetadata(
                forwarded=False,
                email=self._get_message_metadata(attached_message),
            )
        return fp.ForwardMetadata(
            forwarded=False,
            email=self._get_message_metadata(msg),
        )

    def get_original_metadata_from_file(self, file_path: str) -> fp.ForwardMetadata:
        """
        Extract metadata from the original or forwarded email.

        :param file_path: The path to the email file to parse.
        :type file_path: str
        :return: An object containing metadata of the original email.
        :rtype: fp.ForwardMetadata
        """
        return self.get_original_metadata(self._get_file_content(file_path))

    def _get_dict(
        self, message: Message | str, email: fp.OriginalMetadata, forwarded: bool, send_to: str = ""
    ) -> ParsedEmail:
        if forwarded:
            source_message = (
                message if isinstance(message, Message) else self._parse_message(message)
            )
            eml = self._build_original_email(email, source_message).as_string()
        else:
            eml = message.as_string() if isinstance(message, Message) else message
        return {"forward": forwarded, "eml": eml, "Send-To": send_to}

    def _build_original_email(
        self, metadata: fp.OriginalMetadata, message: Message
    ) -> EmailMessage | MIMEMultipart:
        if not message.is_multipart():
            result_message = EmailMessage()
            self._set_headers(metadata, result_message)
            result_message.set_content(metadata.body or "")
            return result_message

        result = MIMEMultipart()
        self._set_headers(metadata, result)

        mt = MIMEText(metadata.body or "", _subtype="plain", _charset="utf-8")
        result.attach(mt)
        raw_payload = message.get_payload()
        if isinstance(raw_payload, list):
            pending = list(raw_payload)
            while pending:
                part = pending.pop(0)
                if isinstance(part, str) or (
                    part.get_content_type() == "text/plain"
                    and "attachment" not in str(part.get("Content-Disposition"))
                ):
                    continue
                if part.get_content_subtype() in ["related", "alternative"]:
                    nested_payload = part.get_payload()
                    if isinstance(nested_payload, list):
                        pending.extend(nested_payload)
                    continue
                if part.get_content_type() == "text/html":
                    part.set_payload(part.get_payload())
                result.attach(part)
        return result

    def _set_headers(self, metadata: fp.OriginalMetadata, result: EmailMessage | Message) -> None:
        if metadata.date:
            result["Date"] = self._header_value(metadata.date)
        from_header = self._format_addresses([metadata.from_])
        if from_header:
            result["From"] = self._header_value(from_header)
        if metadata.subject:
            result["Subject"] = self._header_value(metadata.subject)
        to_header = self._format_addresses(metadata.to)
        if to_header:
            result["To"] = self._header_value(to_header)
        if metadata.cc:
            result["CC"] = self._header_value(self._format_addresses(metadata.cc))

    def _header_value(self, value: str) -> str:
        # Parsed values come from message text, which may hold any Unicode line
        # break (for example U+2028); a header value must be a single line.
        return " ".join(value.splitlines())

    def _format_addresses(self, contacts: list[fp.MailboxResult]) -> str:
        addresses = []
        for contact in contacts:
            name = contact.name.strip()
            address = contact.address.strip()
            if address:
                addresses.append(formataddr((name, address)) if name else address)
            elif name:
                addresses.append(name)
        return ", ".join(addresses)

    def _get_forwarded_metadata(self, message: Message) -> fp.ForwardMetadata:
        body = self._get_body(message)
        subject = message.get("Subject")
        subject = str(subject) if subject is not None else ""
        if subject:
            return fp.get_forwarded_metadata(body.strip(), subject.strip())
        return fp.get_forwarded_metadata(body.strip())

    def _get_body(self, msg: Message) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                if part.is_multipart():
                    continue
                content_type = part.get_content_type()
                content_disposition = part.get_content_disposition()

                if content_type == "text/plain" and content_disposition != "attachment":
                    return self._get_part_text(part)
            return ""
        return self._get_part_text(msg)

    def _get_eml_attachment(self, message: Message) -> str:
        for part in message.walk():
            content_type = part.get_content_type()
            if content_type == "message/rfc822":
                try:
                    payload = part.get_payload()
                    if isinstance(payload, list) and payload:
                        first_message = payload[0]
                        if isinstance(first_message, Message):
                            return first_message.as_string()
                        return str(first_message)

                    get_content = getattr(part, "get_content", None)
                    if callable(get_content):
                        content = get_content()
                        if isinstance(content, Message):
                            return content.as_string()
                except LookupError, TypeError, ValueError:
                    LOGGER.warning("attached_eml_decode_failed")
                    continue
            if content_type == "application/octet-stream":
                file_name = part.get_filename()
                if file_name and file_name.lower().endswith(".eml"):
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        return self._decode_bytes(payload, part.get_content_charset())
                    if isinstance(payload, str):
                        return self.get_decoded_str(payload, part.get_content_charset())
        return ""

    def _get_file_content(self, file_path: str) -> str:
        with open(file_path, encoding="utf8") as file:
            return file.read()

    def _parse_message(self, email: str) -> Message:
        return Parser(policy=policy.default).parsestr(email)

    def _get_message_metadata(self, message: Message) -> fp.OriginalMetadata:
        from_mailboxes = self._mailboxes_from_header(message.get("From", ""))
        return fp.OriginalMetadata(
            date=str(message.get("Date", "")).strip(),
            subject=str(message.get("Subject", "")).strip(),
            body=self._get_body(message).strip(),
            from_=from_mailboxes[0] if from_mailboxes else fp.MailboxResult(),
            to=self._mailboxes_from_header(message.get("To", "")),
            cc=self._mailboxes_from_header(message.get("Cc", "")),
        )

    def _first_header_address(self, header: object) -> str:
        mailboxes = self._mailboxes_from_header(header)
        if not mailboxes:
            return ""
        return mailboxes[0].address or mailboxes[0].name

    def _mailboxes_from_header(self, header: object) -> list[fp.MailboxResult]:
        if not header:
            return []
        contacts = []
        for name, address in getaddresses([str(header)]):
            if name or address:
                contacts.append(fp.prepare_mailbox(name, address))
        return contacts

    def _get_part_text(self, part: Message) -> str:
        get_content = getattr(part, "get_content", None)
        if callable(get_content):
            try:
                content = get_content()
                if isinstance(content, str):
                    return content
                if isinstance(content, bytes):
                    return self._decode_bytes(content, part.get_content_charset())
            except LookupError, TypeError, ValueError:
                LOGGER.warning("message_part_decode_failed", exc_info=True)

        payload = part.get_payload(decode=True)
        if isinstance(payload, bytes):
            return self._decode_bytes(payload, part.get_content_charset())
        if isinstance(payload, str):
            return self.get_decoded_str(payload, part.get_content_charset())

        payload = part.get_payload()
        return payload if isinstance(payload, str) else ""

    def _decode_bytes(self, payload: bytes, charset: str | None = None) -> str:
        try:
            return payload.decode(charset or "utf-8", errors="replace")
        except LookupError, UnicodeError:
            # The sender declared a charset Python does not know (for example
            # "unknown-8bit") or a codec that is not a text encoding.
            return payload.decode("utf-8", errors="replace")

    def get_decoded_str(self, s: str | bytes | None, charset: str | None = None) -> str:
        if s is None:
            return ""
        if isinstance(s, bytes):
            return self._decode_bytes(s, charset)
        compact = "".join(s.split())
        try:
            return self._decode_bytes(base64.b64decode(compact, validate=True), charset)
        except binascii.Error, ValueError:
            return s
