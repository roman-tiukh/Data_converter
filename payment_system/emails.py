from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from payment_system.models import ProjectSubscription, Project, Subscription, UserProject, Invoice

from django.conf import settings

from data_converter.email_utils import send_template_mail
from users.models import DataOceanUser


def member_activated(user: 'DataOceanUser', project: 'Project'):
    send_template_mail(
        to=[user.email],
        subject='Доступ до проєкту відновлено',
        template='payment_system/emails/member_activated.html',
        context={
            'user': user,
            'project': project,
        },
    )


def member_removed(user: 'DataOceanUser', project: 'Project'):
    send_template_mail(
        to=[user.email],
        subject='Вас видалили з проєкту',
        template='payment_system/emails/member_removed.html',
        context={
            'user': user,
            'project': project,
        },
    )


def membership_confirmed(user: 'DataOceanUser', member: DataOceanUser):
    send_template_mail(
        to=[user.email],
        subject='Користувач, якого Ви додали до проєкту, підтвердив ваше запрошення',
        template='payment_system/emails/membership_confirmed.html',
        context={
            'user': user,
            'member': member,
        },
    )


def new_invitation(invited_email: str, project: 'Project'):
    is_user_exists = DataOceanUser.objects.filter(email=invited_email).exists()
    frontend_link = settings.FRONTEND_SITE_URL
    send_template_mail(
        to=[invited_email],
        subject='Вас запросили до нового проєкту',
        template='payment_system/emails/new_invitation.html',
        context={
            'project': project,
            'is_user_exists': is_user_exists,
            'frontend_link': frontend_link,
        },
    )


# TODO: Add here PDF document as attachment
def new_invoice(invoice: 'Invoice', project: 'Project'):
    owner = project.owner
    pdf = invoice.get_pdf()
    send_template_mail(
        to=[owner.email],
        subject='Рахунок на оплату',
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


def new_subscription(project_subscription: 'ProjectSubscription'):
    owner = project_subscription.project.owner
    send_template_mail(
        to=[owner.email],
        subject='Ви підписалися на новий тарифний план',
        template='payment_system/emails/new_subscription.html',
        context={
            'user': owner,
            'project_subscription': project_subscription,
        },
    )


def payment_confirmed(project_subscription: 'ProjectSubscription'):
    owner = project_subscription.project.owner
    send_template_mail(
        to=[owner.email],
        subject='Оплату підтверджено',
        template='payment_system/emails/payment_confirmed.html',
        context={
            'user': owner,
            'project': project_subscription.project,
            'subscription': project_subscription.subscription,
        },
    )


def project_non_payment(project: 'Project'):
    from payment_system.models import Subscription
    default_subscription = Subscription.get_default_subscription()
    owner = project.owner
    send_template_mail(
        to=[owner.email],
        subject='Ваш проєкт переведено на безкоштовний тарифний план через несплату',
        template='payment_system/emails/project_non_payment.html',
        context={
            'user': owner,
            'project': project,
            'default_subscription': default_subscription,
        },
    )


def token_has_been_changed(project: 'Project'):
    from payment_system.models import UserProject
    users = project.users.exclude(
        user_projects__role=UserProject.OWNER,
        user_projects__status=UserProject.DEACTIVATED,
    ).values_list('email', flat=True)

    send_template_mail(
        to=users,
        subject='Токен у проєкті був змінений',
        template='payment_system/emails/token_has_been_changed.html',
        context={
            'project': project,
        },
    )


def tomorrow_payment_day(project_subscription: 'ProjectSubscription'):
    owner = project_subscription.project.owner
    invoice = project_subscription.latest_invoice
    if not invoice or invoice.is_paid:
        return
    pdf = invoice.get_pdf()
    send_template_mail(
        to=[owner.email],
        subject='У Вас не оплачено рахунок',
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
