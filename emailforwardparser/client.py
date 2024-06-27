import json
import re
from email.message import EmailMessage, Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import Parser

from emailforwardparser import forward_parser as fp


class EmailParserClient:
    """
    A client for parsing email messages, with support for detecting and handling forwarded emails.
    """

    def get_original_eml(self, email: str) -> dict:
        """
        Retrieve the original email message as a dict, including metadata and content.

        :param email: Contents of email to be parsed.
        :type email: str
        :return: A dictionary containing the email metadata and content.
        :rtype: dict
        """
        msg = Parser().parsestr(email)
        original_metadata = self._get_forwarded_metadata(msg)
        if not original_metadata.forwarded:
            eml = self._get_eml_attachment(msg)
            if eml:
                original_metadata = self._get_forwarded_metadata(eml)
                msg = eml
        return self._get_dict(msg, original_metadata.email, original_metadata.forwarded)

    def get_original_eml_from_file(self, file_path: str) -> dict:
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
        msg = Parser().parsestr(email)
        original_metadata = self._get_forwarded_metadata(msg)
        if not original_metadata.forwarded:
            eml = self._get_eml_attachment(msg)
            if eml:
                original_metadata = self._get_forwarded_metadata(eml)
        return original_metadata

    def get_original_metadata_from_file(self, file_path: str) -> fp.ForwardMetadata:
        """
        Extract metadata from the original or forwarded email.

        :param file_path: The path to the email file to parse.
        :type file_path: str
        :return: An object containing metadata of the original email.
        :rtype: fp.ForwardMetadata
        """
        msg = Parser().parsestr(self._get_file_content(file_path))
        return self._get_forwarded_metadata(msg)

    def _get_dict(self, message: Message, email: fp.OriginalMetadata, forwarded: bool) -> dict:
        result = {}
        if forwarded:
            result["Send-To"] = email.to[0].address
            result["eml"] = self._build_original_email(email, message).as_string()
        else:
            result["Send-To"] = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', message.get("From")).group(0)
            result["eml"] = message.as_string()
        return result

    def _build_original_email(self, metadata: fp.OriginalMetadata, message: Message) -> EmailMessage | MIMEMultipart:
        if not message.is_multipart():
            result_message = EmailMessage()
            self._set_headers(metadata, message, result_message)
            result_message.set_content(metadata.body)
            return result_message

        result = MIMEMultipart()
        self._set_headers(metadata, message, result)

        if metadata.cc:
            result["CC"] = self._format_addresses(metadata.cc)

        mt = MIMEText(None, _subtype="plain", _charset="utf-8")
        mt.replace_header("content-transfer-encoding", "quoted-printable")
        mt.set_payload(metadata.body)
        result.attach(mt)
        payload = message.get_payload()
        if isinstance(payload, list):
            for part in payload:
                if (part.get_content_type() == 'text/plain'
                        and 'attachment' not in str(part.get('Content-Disposition'))):
                    continue
                result.attach(part)
        return result

    def _set_headers(self, metadata: fp.OriginalMetadata, message: Message, result: EmailMessage | Message) -> None:
        result["Date"] = metadata.date
        result["From"] = metadata.from_.address
        result["Subject"] = metadata.subject
        result["To"] = self._format_addresses(metadata.to)
        if metadata.cc:
            result["CC"] = self._format_addresses(metadata.cc)

    def _format_addresses(self, contacts: list[fp.MailboxResult]) -> str:
        result = contacts[0].address
        for index in range(1, len(contacts)):
            result += ", " + contacts[index].address
        return result

    def _get_forwarded_metadata(self, message: Message) -> fp.ForwardMetadata:
        body = self._get_body(message)
        subject = message.get("Subject")
        subject = subject if subject is not None else ""
        if subject:
            return fp.get_forwarded_metadata(body.strip(), subject.strip())
        return fp.get_forwarded_metadata(body.strip())

    def _get_body(self, msg: Message) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))

                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    body = part.get_payload()
                    break
        else:
            body = msg.get_payload()

        return body if isinstance(body, str) else ""

    def _get_eml_attachment(self, message: Message) -> Message | None:
        for part in message.walk():
            file_name = part.get_filename()
            if (file_name is not None and file_name.endswith(".eml")):
                return part.get_payload()[0]
        return None

    def _get_file_content(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf8") as file:
            return file.read()
