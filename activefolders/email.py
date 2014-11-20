from __future__ import absolute_import
from email.mime.text import MIMEText
from smtplib import SMTP
import activefolders.conf as conf


class Message:
    def __init__(self, subject, body, recipient):
        super().__init__()
        self._message = MIMEText(body)
        self._message['Subject'] = subject
        self._message['From'] = None
        self._message['To'] = recipient

    def send(self):
        if self._message['To'] is None:
            return

        smtp_server = conf.settings['dtnd'].get('smtp_server')
        if smtp_server is None:
            return

        with SMTP(smtp_server) as smtp:
            smtp.send_message(self._message)


class TransferFailedMessage(Message):
    def __init__(self, transfer):
        uuid = transfer.folder.uuid
        body = "Folder {} could not be transferred to the home DTN of its destination.".format(uuid)
        subject = "Transfer failed"
        recipient = transfer.email
        super().__init__(subject, body, recipient)


class ExportFailedMessage(Message):
    def __init__(self, export):
        uuid = export.folder_destination.folder.uuid
        destination = export.folder_destination.destination
        body = "Folder {} could not exported to destination {}. Please make sure your credentials are correct and try again.".format(uuid, destination)
        subject = "Export failed"
        recipient = export.email
        super().__init__(subject, body, recipient)
