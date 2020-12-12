from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string


class EmailBackend(BaseEmailBackend):

    def __init__(self, fail_silently=False, api_key=None, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = api_key or settings.SENDGRID_API_KEY

    def send_messages(self, email_messages):
        for mess in email_messages:
            mess: EmailMessage = mess
            mess.content_subtype
            mess
            message = mess.message()
            to = mess.to
            cc = mess.cc
            bcc = mess.bcc
            from_email = mess.from_email
            recipients = mess.recipients()

            # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            # from_email = Email("test@example.com")
            # to_email = To("test@example.com")
            # subject = "Sending with SendGrid is Fun"
            # content = Content("text/plain", "and easy to do anywhere, even with Python")
            # mail = Mail(from_email, to_email, subject, content)
            # response = sg.client.mail.send.post(request_body=mail.get())

            mess


def send_template_mail(to, subject, template, context, asynchronously=True):
    """ here you render template to string and send asynchronously email (Thread) """
    html = render_to_string(template, context)
    if asynchronously:
        """ send asynchronously email (Thread) """
    else:
        e = EmailMessage(
            to='to@admin.com',
            from_email='asdasd',
            body=html,
        )
        e.content_subtype = 'html'
        e.send()
        # ------ or ---------
        send_mail(
            # ...
            html_message=html,
            # ...
        )


def send_project_create_message(to):
    send_template_mail(
        subject='hello',
        template='some/template/here.html',
        context={
            "one": 1,
            "two": 2,
        }
    )


def send_project_create_message(to):
    send_template_mail(
        subject='hello',
        template='some/template/here.html',
        context={
            "one": 1,
            "two": 2,
        }
    )


def send_project_disable_message(to):
    send_template_mail(
        subject='hello',
        template='some/template/here.html',
        context={
            "one": 1,
            "two": 2,
        }
    )
