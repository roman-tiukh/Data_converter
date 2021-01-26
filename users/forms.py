import re

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm

from users import emails
from .models import DataOceanUser


class CustomPasswordResetForm(PasswordResetForm):

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Custom send confirmation email for password reset.
        """

        # check if this email is among existing users
        user = DataOceanUser.objects.filter(email=context['email']).first()
        if user:
            # create a confirm_link to the user to confirm the password reset
            domain = re.sub(r'/$', '', settings.FRONTEND_SITE_URL)
            confirm_link = f"{domain}/auth/restore-pass/confirmation/{context['uid']}/{context['token']}/"
            # send mail
            emails.send_reset_password_message(user, confirm_link)
