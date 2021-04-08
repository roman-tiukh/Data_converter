from typing import TYPE_CHECKING

from django.utils import translation, timezone

if TYPE_CHECKING:
    from payment_system.models import (
        ProjectSubscription,
        Project,
        Subscription,
        UserProject,
        Invoice,
        CustomSubscriptionRequest,
        Invitation,
        InvoiceReport,
    )

from django.conf import settings

from data_converter.email_utils import send_template_mail
from users.models import DataOceanUser
from django.utils.translation import gettext_lazy as _, gettext


def member_deleted(user: 'DataOceanUser', project: 'Project'):  # 6
    with translation.override(user.language):
        user.notify(message=gettext('You have been deleted from the project') + f' "{project.name}"')
        send_template_mail(
            to=[user.email],
            subject=_('You were deleted from the project'),
            template='payment_system/emails/member_deleted.html',
            context={
                'user': user,
                'project': project,
            },
        )


def member_activated(user: 'DataOceanUser', project: 'Project'):  # 5
    with translation.override(user.language):
        user.notify(
            message=gettext("You have been restored an access to the project") + f' "{project.name}"',
            link=project.frontend_link,
        )
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
    with translation.override(user.language):
        user.notify(message=gettext('You have been removed from the project') + f' "{project.name}"')
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
    with translation.override(user.language):
        user.notify(message=f'{member.get_full_name()} ' + gettext('confirm your invitation'))
        send_template_mail(
            to=[user.email],
            subject=_('The user you added to the project will confirm your invitation'),
            template='payment_system/emails/membership_confirmed.html',
            context={
                'user': user,
                'member': member,
            },
        )


def new_invitation(invitation: 'Invitation'):  # 2
    invited_email = invitation.email
    project = invitation.project
    user = DataOceanUser.objects.filter(email=invited_email).first()
    if user:
        user.notify(
            message=_('The user {owner} has invited you to the project "{project}"').format(
                owner=project.owner.get_full_name(),
                project=project.name,
            ),
            link=project.frontend_projects_link,
        )
    frontend_link = settings.FRONTEND_SITE_URL
    if user:
        lang = user.language
    else:
        lang = project.owner.language
    with translation.override(lang):
        send_template_mail(
            to=[invited_email],
            subject=_('You have been invited to a new project'),
            template='payment_system/emails/new_invitation.html',
            context={
                'project': project,
                'is_user_exists': bool(user),
                'frontend_link': frontend_link,
            },
        )


def new_invoice(invoice: 'Invoice', project: 'Project'):  # 7
    owner = project.owner
    with translation.override(owner.language):
        owner.notify(
            message=_(
                'According to the terms of your subscription '
                'today you need to pay for the project %(project)s'
            ) % {'project': project.name},
            link=f'{settings.BACKEND_SITE_URL}{invoice.link}'
        )
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
    with translation.override(owner.language):
        owner.notify(
            message=gettext('You have subscribed to the subscription') + f' "{project_subscription.subscription.name}"'
        )
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
    with translation.override(owner.language):
        owner.notify(
            message=gettext('We confirm payment for the project') + f' "{project_subscription.project.name}"',
            link=f'{settings.BACKEND_SITE_URL}{project_subscription.latest_invoice.link}'
        )
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
    with translation.override(owner.language):
        owner.notify(
            message=_(
                "Due to non-payment of the project %(project)s, "
                "it has been transferred to the free subscription without the possibility of its change. "
                "To resume work with previous conditions, please connect our support."
            ) % {'project': project.name},
            link=project.frontend_link,
        )
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
    ).exclude(
        user_projects__status=UserProject.DEACTIVATED,
    )

    for user in users:
        with translation.override(user.language):
            user.notify(
                message=_('Note that the token in the project {project} has been changed').format(
                    project=project.name,
                ),
                link=project.frontend_link,
            )

    send_template_mail(
        to=[user.email for user in users],
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
    with translation.override(owner.language):
        send_template_mail(
            to=[owner.email],
            subject=_('You have not paid the bill'),
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


def new_custom_sub_request(custom_subscription_request: 'CustomSubscriptionRequest'):
    send_template_mail(
        to=[settings.SUPPORT_EMAIL],
        subject=f'Запит на тарифний план Custom від {custom_subscription_request.full_name}',
        template='payment_system/emails/new_custom_sub_request.html',
        context={
            'csr': custom_subscription_request,
        },
    )


def create_report(invoices: dict):
    send_template_mail(
        to=[settings.SUPPORT_EMAIL],
        subject=f'Підсумок оплати інвойсів за {timezone.localdate()}',
        template='payment_system/emails/daily_report.html',
        context={
            'should_complete_invoices': invoices['should_complete'],
            'was_overdue_invoices': invoices['was_overdue'],
            'was_overdue_grace_period_invoices': invoices['was_overdue_grace_period'],
            'was_complete_invoices': invoices['was_complete'],
        },
    )
