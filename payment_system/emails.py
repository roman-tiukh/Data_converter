from data_converter.email_utils import send_template_mail
from payment_system.models import ProjectSubscription, Project, Invoice
from users.models import DataOceanUser


# FIXME: subscription_link?
def send_new_subscription_message(user: DataOceanUser, project_subscription: ProjectSubscription,
                                  subscription_link, ):
    send_template_mail(
        to=[user.email],
        subject='Ви підписалися на новий пакет послуг',
        template='payment_system/emails/new_subscription.html',
        context={
            'user': user,
            'subscription_link': subscription_link,
            'project_subscription': project_subscription,
            'FUTURE': ProjectSubscription.FUTURE,
        }
    )


# FIXME: invited member dont have name, only email.
def send_invited_member_message(user: DataOceanUser, project: Project, member: DataOceanUser):
    send_template_mail(
        to=[user.email],
        subject='Ви додали нового користувача до проєкту',
        template='payment_system/emails/invited_member.html',
        context={
            'user': user,
            'project': project,
            'member': member
        }
    )


# FIXME: we dont have confirm_link, only accept in UI, and user can be not registered
def send_confirm_membership_message(user: DataOceanUser, owner: DataOceanUser,
                                    project: Project, confirm_link):
    send_template_mail(
        to=[user.email],
        subject='Вас запросили до нового проєкту',
        template='payment_system/emails/confirm_membership.html',
        context={
            'user': user,
            'owner': owner,
            'project_name': project,
            'confirm_link': confirm_link
        }
    )


# FIXME: link = settings.FRONTEND_URL?
def send_project_token_message(user: DataOceanUser, link):
    send_template_mail(
        to=[user.email],
        subject='Доступ до токена',
        template='payment_system/emails/project_token.html',
        context={
            'user': user,
            'link': link
        }
    )


def send_membership_confirmed_message(user: DataOceanUser, member: DataOceanUser):
    send_template_mail(
        to=[user.email],
        subject='Користувач, якого Ви додали до проєкту, підтвердив ваше запрошення',
        template='payment_system/emails/membership_confirmed.html',
        context={
            'user': user,
            'member': member,
        }
    )


# FIXME: видалили?
def send_removed_member_message(user: DataOceanUser, member: DataOceanUser, project: Project):
    send_template_mail(
        to=[user.email],
        subject='Ви видалили користувача з проєкту',
        template='payment_system/emails/removed_member.html',
        context={
            'user': user,
            'member': member,
            'project': project
        }
    )


# FIXME: видалили?
def send_membership_removed_message(user: DataOceanUser, owner: DataOceanUser, project: Project):
    send_template_mail(
        to=[user.email],
        subject='Вас видалили із проєкту',
        template='payment_system/emails/membership_removed.html',
        context={
            'user': user,
            'owner': owner,
            'project': project
        }
    )


# TODO: create property in Invoice model - frontend_link
def send_new_invoice_message(user: DataOceanUser, invoice: Invoice, invoice_link: str):
    send_template_mail(
        to=[user.email],
        subject='Новий рахунок',
        template='payment_system/emails/new_invoice.html',
        context={
            'user': user,
            'invoice': invoice,
            'invoice_link': invoice_link,
        }
    )
