from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail as send_backend_mail
from django.conf import settings
from .models import DataOceanUser
from postman import send_plain_mail


class CustomPasswordResetForm(PasswordResetForm):

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Custom send confirmation email for password reset.
        """

        # check if this email is among existing users
        if DataOceanUser.objects.filter(email=context['email']).exists():
            # create a letter to the user to confirm the password reset
            confirm_link = f"{settings.FRONTEND_SITE_URL}/api/rest-auth/password/reset/confirm/{context['uid']}/{context['token']}"
            subject = 'Скидання пароля користувача на Data Ocean'
            text = f"Вітаємо! \r\nВи замовили скидання пароля у системі Data Ocean. \r\nЛінк підтвердження: {confirm_link} \r\nЯкщо Вами ці дії не проводились, проігноруйте цей лист."
            # send mail
            if settings.SEND_MAIL_BY_POSTMAN:
                # use POSTMAN
                send_plain_mail(context['email'], subject, text)
            else:
                # use EMAIL_BACKEND
                send_backend_mail(subject, text, settings.DEFAULT_FROM_EMAIL, [context['email'], ], fail_silently=True)
