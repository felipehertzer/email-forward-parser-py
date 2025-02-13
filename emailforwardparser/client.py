import re
import json
import base64
import logging
from email.message import EmailMessage, Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import Parser
from typing import Any

from emailforwardparser import forward_parser as fp


log = logging.getLogger('emailforwardparser')
EMAIL_ADDR_REGEX = re.compile(r'[\w.+-]+@[\w-]+\.*[\w.-]+')


class EmailParserClient:
    """
    A client for parsing email messages, with support for detecting and handling forwarded emails.
    """

    def get_original_eml(self, email: str) -> dict:
        """
        Retrieve the original email message as a dict, including metadata and content.

        If any field contains invalid data, the empty string will replace it.

        :param email: Contents of email to be parsed.
        :type email: str
        :return: A dictionary containing the email metadata and content.
        :rtype: dict
        """
        msg = Parser().parsestr(email)
        matches = EMAIL_ADDR_REGEX.search(msg.get("From", ''))
        send_to = matches.group(0) if matches else ''
        eml = self._get_eml_attachment(msg)
        if eml:
            return self._get_dict(eml, fp.OriginalMetadata(), False, send_to=send_to)
        original_metadata = self._get_forwarded_metadata(msg)
        return self._get_dict(msg, original_metadata.email, original_metadata.forwarded, send_to=send_to)

    def get_original_eml_json(self, email: str) -> str:
        """
        Retrieve the original email message as a JSON string, including metadata and content.

        :param email: Contents of email to be parsed.
        :type email: str
        :return: A JSON string containing the email metadata and content.
        :rtype: str
        """
        return json.dumps(self.get_original_eml(email))

    def get_original_eml_from_file(self, file_path: str) -> dict:
        """
        Retrieve the original email message as a JSON str, including metadata and content.

        :param file_path: The path to the email file to parse.
        :type file_path: str
        :return: A dictionary containing the original receiver and eml content.
        :rtype: dict
        """
        return self.get_original_eml(self._get_file_content(file_path))

    def get_original_eml_json_from_file(self, file_path: str) -> str:
        """
        Retrieve the original email message as a JSON str, including metadata and content.

        :param file_path: The path to the email file to parse.
        :type file_path: str
        :return: A JSON string containing the email metadata and content.
        :rtype: str
        """
        return json.dumps(self.get_original_eml(self._get_file_content(file_path)))

    def get_original_metadata(self, file_path: str) -> fp.ForwardMetadata:
        """
        Extract metadata from the original or forwarded email.

        :param file_path: The path to the email file to parse.
        :type file_path: str
        :return: An object containing metadata of the original email.
        :rtype: fp.ForwardMetadata
        """
        msg = Parser().parsestr(self._get_file_content(file_path))
        return self._get_forwarded_metadata(msg)

    def _get_dict(self, message: Message | str, email: fp.OriginalMetadata, forwarded: bool, send_to: str = '') -> dict:
        result: dict[str, Any] = {}
        result['forward'] = forwarded
        if forwarded:
            result["eml"] = self._build_original_email(email, message).as_string()
        else:
            if isinstance(message, Message):
                result["eml"] = message.as_string()
            else:
                result['eml'] = message
        result['Send-To'] = send_to
        return result

    def _build_original_email(self, metadata: fp.OriginalMetadata, message: Message) -> EmailMessage | MIMEMultipart:
        if not message.is_multipart():
            result_message = EmailMessage()
            self._set_headers(metadata, result_message)
            result_message.set_content(metadata.body)
            return result_message

        result = MIMEMultipart()
        self._set_headers(metadata, result)

        if metadata.cc:
            result["CC"] = self._format_addresses(metadata.cc)

        mt = MIMEText(None, _subtype="plain", _charset="utf-8")  # type: ignore
        mt.replace_header("content-transfer-encoding", "quoted-printable")
        mt.set_payload(metadata.body)
        result.attach(mt)
        payload = message.get_payload()
        if isinstance(payload, list):
            for part in payload:
                if isinstance(part, str) or (part.get_content_type() == 'text/plain'
                                             and 'attachment' not in str(part.get('Content-Disposition'))):
                    continue
                if part.get_content_subtype() in ['related', 'alternative']:
                    payload.extend(part.get_payload())
                    continue
                if part.get_content_type() == 'text/html':
                    part.set_payload(part.get_payload())
                result.attach(part)
        return result

    def _set_headers(self, metadata: fp.OriginalMetadata, result: EmailMessage | Message) -> None:
        result["Date"] = metadata.date
        result["From"] = metadata.from_.address
        result["Subject"] = metadata.subject
        result["To"] = self._format_addresses(metadata.to)
        if metadata.cc:
            result["CC"] = self._format_addresses(metadata.cc)

    def _format_addresses(self, contacts: list[fp.MailboxResult]) -> str:
        if contacts:
            result = contacts[0].address
            for index in range(1, len(contacts)):
                result += ", " + contacts[index].address
            return result
        return ''

    def _get_forwarded_metadata(self, message: Message) -> fp.ForwardMetadata:
        body = self._get_body(message)
        subject = message.get("Subject")
        subject = subject if subject is not None else ""
        if subject:
            return fp.get_forwarded_metadata(body.strip(), subject.strip())
        return fp.get_forwarded_metadata(body.strip())

    def _get_body(self, msg: Message) -> str:
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))

                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    body = self.get_decoded_str(part.get_payload())
                    break
        else:
            body = self.get_decoded_str(msg.get_payload())
        return body if isinstance(body, str) else ""

    def _get_eml_attachment(self, message: Message) -> str:
        for part in message.walk():
            content_type = part.get_content_type()
            if content_type is not None and content_type == 'message/rfc822':
                try:
                    return part.get_payload()[0].as_string()
                except Exception:
                    log.warning('failed to get attached eml, looking for others')
                    continue
            if content_type is not None and content_type == 'application/octet-stream':
                file_name = part.get_filename()
                if file_name and file_name.endswith('.eml'):
                    return base64.b64decode(part.get_payload()).decode()
        return ''

    def _get_file_content(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf8") as file:
            return file.read()

    def get_decoded_str(self, s) -> str:
        try:
            return base64.b64decode(s).decode()
        except Exception:
            return s
