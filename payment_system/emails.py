from typing import TYPE_CHECKING

from django.utils import translation

if TYPE_CHECKING:
    from payment_system.models import ProjectSubscription, Project, Subscription, UserProject, Invoice

from django.conf import settings

from data_converter.email_utils import send_template_mail
from users.models import DataOceanUser
from django.utils.translation import gettext_lazy as _


def member_activated(user: 'DataOceanUser', project: 'Project'):  # 5
    send_template_mail(
        to=[user.email],
        subject=_('Access to the project is restored'),
        template='payment_system/emails/member_activated.html',
        context={
            'user': user,
            'project': project,
        },
    )


def member_removed(user: 'DataOceanUser', project: 'Project'):  # 4
    send_template_mail(
        to=[user.email],
        subject=_('You were expelled from the project'),
        template='payment_system/emails/member_removed.html',
        context={
            'user': user,
            'project': project,
        },
    )


def membership_confirmed(user: 'DataOceanUser', member: DataOceanUser):  # 3
    send_template_mail(
        to=[user.email],
        subject=_('The user you added to the project will confirm your invitation'),
        template='payment_system/emails/membership_confirmed.html',
        context={
            'user': user,
            'member': member,
        },
    )


def new_invitation(invited_email: str, project: 'Project'):  # 2
    is_user_exists = DataOceanUser.objects.filter(email=invited_email).exists()
    frontend_link = settings.FRONTEND_SITE_URL
    lang = project.owner.language
    with translation.override(lang):
        send_template_mail(
            to=[invited_email],
            subject=_('You have been invited to a new project'),
            template='payment_system/emails/new_invitation.html',
            context={
                'project': project,
                'is_user_exists': is_user_exists,
                'frontend_link': frontend_link,
            },
        )


def new_invoice(invoice: 'Invoice', project: 'Project'):  # 7
    owner = project.owner
    pdf = invoice.get_pdf()
    send_template_mail(
        to=[owner.email],
        subject=_('Invoice for payment'),
        template='payment_system/emails/new_invoice.html',
        context={
            'user': owner,
            'project': project,
        },
        attachments=[
            (
                pdf.name,
                pdf.read(),
                'application/pdf',
            ),
        ],
    )


def new_subscription(project_subscription: 'ProjectSubscription'):  # 1
    owner = project_subscription.project.owner
    send_template_mail(
        to=[owner.email],
        subject=_('You have subscribed to a new subscription'),
        template='payment_system/emails/new_subscription.html',
        context={
            'user': owner,
            'project_subscription': project_subscription,
        },
    )


def payment_confirmed(project_subscription: 'ProjectSubscription'):  # 10
    owner = project_subscription.project.owner
    send_template_mail(
        to=[owner.email],
        subject=_('Payment confirmed'),
        template='payment_system/emails/payment_confirmed.html',
        context={
            'user': owner,
            'project': project_subscription.project,
            'subscription': project_subscription.subscription,
        },
    )


def project_non_payment(project: 'Project'):  # 9
    from payment_system.models import Subscription
    default_subscription = Subscription.get_default_subscription()
    owner = project.owner
    send_template_mail(
        to=[owner.email],
        subject=_('Your project has been transferred to a free subscription due to non-payment'),
        template='payment_system/emails/project_non_payment.html',
        context={
            'user': owner,
            'project': project,
            'default_subscription': default_subscription,
        },
    )


def token_has_been_changed(project: 'Project'):  # 6
    from payment_system.models import UserProject
    users = project.users.exclude(
        user_projects__role=UserProject.OWNER,
        user_projects__status=UserProject.DEACTIVATED,
    ).values_list('email', flat=True)

    send_template_mail(
        to=users,
        subject=_('Token access has been changed in the project'),
        template='payment_system/emails/token_has_been_changed.html',
        context={
            'project': project,
        },
    )


def tomorrow_payment_day(project_subscription: 'ProjectSubscription'):  # 8
    owner = project_subscription.project.owner
    invoice = project_subscription.latest_invoice
    if not invoice or invoice.is_paid:
        return
    pdf = invoice.get_pdf()
    send_template_mail(
        to=[owner.email],
        subject=_('You have not paid the invoice'),
        template='payment_system/emails/tomorrow_payment_day.html',
        context={
            'user': owner,
            'project': project_subscription.project,
        },
        attachments=[
            (
                pdf.name,
                pdf.read(),
                'application/pdf',
            ),
        ],
    )
