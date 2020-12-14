import logging
from threading import Thread

import sendgrid
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend
from django.template.loader import render_to_string
from python_http_client.exceptions import HTTPError
from sendgrid.helpers.mail import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SendGridEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = settings.SENDGRID_API_KEY

    def send_messages(self, email_messages):
        sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
        for email_message in email_messages:
            from_email = Email(email_message.from_email)
            to_email = To(email_message.to)
            subject = email_message.subject
            html_content = HtmlContent(email_message.body)
            mail = Mail(from_email=from_email, to_emails=to_email, subject=subject,
                        html_content=html_content)
            try:
                response = sg.client.mail.send.post(request_body=mail.get())
                if response.status_code // 100 != 2:
                    logger.error(f'Email "{subject}" was not sent to{email_message.to}. '
                                 f'Status is {response.status_code}')
            except HTTPError as error:
                logger.exception(f'Email {subject} was not sent to{email_message.to} - {error}')


def send_template_mail(to, subject, template, context, asynchronously=True,
                       from_email=None):
    html = render_to_string(template, context)
    e_message = EmailMessage(
        subject=subject,
        body=html,
        from_email=from_email,
        to=to,
    )
    e_message.content_subtype = 'html'
    if not asynchronously:
        e_message.send()
    else:
        # we have toe use Celery here
        Thread(target=e_message.send).start()
