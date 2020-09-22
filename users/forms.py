import re
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail as send_backend_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import DataOceanUser
from data_ocean.postman import send_plain_mail

PASSWORD_RESET_SUBJECT = 'Скидання пароля користувача на Data Ocean'
PASSWORD_RESET_MSG = (
    "Вітаємо! \r\n"
    "Ви замовили скидання пароля у системі Data Ocean. \r\n"
    "Лінк підтвердження: \r\n"
    "{confirm_link} \r\n"
    "Якщо Вами ці дії не проводились, проігноруйте цей лист."
)


class CustomPasswordResetForm(PasswordResetForm):

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Custom send confirmation email for password reset.
        """

        # check if this email is among existing users
        if DataOceanUser.objects.filter(email=context['email']).exists():
            # create a letter to the user to confirm the password reset
            domain = re.sub(r'/$', '', settings.FRONTEND_SITE_URL)
            confirm_link = f"{domain}/auth/restore-pass/confirmation/{context['uid']}/{context['token']}/"
            message = PASSWORD_RESET_MSG.format(confirm_link=confirm_link)
            template_html = render_to_string(
                'users/emails/password_reset.html',
                context={'confirm_link': confirm_link}
            )
            # send mail
            if settings.SEND_MAIL_BY_POSTMAN:
                # use POSTMAN
                send_plain_mail(context['email'], PASSWORD_RESET_SUBJECT, message)
            else:
                # use EMAIL_BACKEND
                send_backend_mail(
                    subject=PASSWORD_RESET_SUBJECT,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=(context['email'],),
                    fail_silently=True,
                    html_message=template_html,
                )
