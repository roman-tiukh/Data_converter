from threading import Thread
from typing import List

from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_template_mail(to: [str], subject: str, template: str, context: dict,
                       from_email: str = None, fail_silently: bool = True,
                       asynchronously: bool = True, attachments: List[tuple] = ()):
    html = render_to_string(template, context)
    e_message = EmailMessage(
        subject=str(subject),
        body=html,
        from_email=from_email,
        to=to,
    )
    e_message.content_subtype = 'html'
    for attachment in attachments:
        e_message.attach(
            filename=attachment[0],
            content=attachment[1],
            mimetype=attachment[2],
        )
    if not asynchronously:
        e_message.send(fail_silently=fail_silently)
    else:
        # TODO: we have to use Celery here
        Thread(
            target=e_message.send,
            kwargs={'fail_silently': fail_silently}
        ).start()
