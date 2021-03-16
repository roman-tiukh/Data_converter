import logging
import base64

import sendgrid
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from python_http_client.exceptions import HTTPError, ForbiddenError
from sendgrid.helpers.mail import Mail, HtmlContent, Attachment


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SendGridBadStatusError(Exception):
    pass


class EmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = settings.SENDGRID_API_KEY

    def send_messages(self, email_messages):
        sg = sendgrid.SendGridAPIClient(api_key=self.api_key)

        for email_message in email_messages:
            mail = Mail(
                from_email=email_message.from_email,
                to_emails=email_message.to,
                subject=email_message.subject,
                html_content=HtmlContent(email_message.body),
            )
            for attachment in email_message.attachments:
                mail.add_attachment(Attachment(
                    file_name=attachment[0],
                    file_content=base64.b64encode(attachment[1]).decode(),
                    file_type=attachment[2],
                ))
            try:
                response = sg.client.mail.send.post(request_body=mail.get())
                if response.status_code // 100 != 2:
                    error_message = (
                        f'Email "{email_message.subject}" was not sent to {email_message.to}. '
                        f'Status is {response.status_code}'
                    )
                    if self.fail_silently:
                        logger.error(error_message)
                    else:
                        raise SendGridBadStatusError(error_message)
            except HTTPError as error:
                if self.fail_silently:
                    if type(error) == ForbiddenError:
                        logger.exception(f'Email {email_message.subject} was not sent to {email_message.to} - {error.to_dict}')
                    else:
                        logger.exception(f'Email {email_message.subject} was not sent to {email_message.to} - {error}')
                else:
                    raise
