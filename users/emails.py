from data_converter.email_utils import send_template_mail
from payment_system.models import Project
from users.models import DataOceanUser, CandidateUserModel
from django.utils.translation import ugettext_lazy as _


def send_confirm_email_message(user: CandidateUserModel, confirm_link: str):
    send_template_mail(
        to=[user.email],
        subject=_('Confirmation of registration in Data Ocean'),
        template='users/emails/confirm_email.html',
        context={
            'user': user,
            'confirm_link': confirm_link
        }
    )


def send_registration_confirmed_message(user: DataOceanUser, default_project: Project):
    send_template_mail(
        to=[user.email],
        subject=_('Welcome to Data Ocean!'),
        template='users/emails/registration_confirmed.html',
        context={
            'user': user,
            'default_project': default_project,
        }
    )


def send_reset_password_message(user: DataOceanUser, confirm_link):
    send_template_mail(
        to=[user.email],
        subject=_('Password reset'),
        template='users/emails/reset_password.html',
        context={
            'user': user,
            'confirm_link': confirm_link
        }
    )
