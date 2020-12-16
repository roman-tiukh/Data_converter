from data_converter.email_backend import send_template_mail

TARIFFS_LINK = 'link'


def send_confirm_email_message(user, confirm_link):
    send_template_mail(
        to=[user.email, ],
        subject='Підтвердження реєстрації у Data Ocean',
        template='users/emails/confirm_email.html',
        context={
            'user_name': user.first_name,
            'confirm_link': confirm_link
        }
    )


def send_registration_confirmed_message(user, default_project_link):
    send_template_mail(
        to=[user.email, ],
        subject='Вітаємо у Data Ocean!',
        template='users/emails/registration_confirmed.html',
        context={
            'user_name': user.first_name,
            'default_project_link': default_project_link,
            'tariffs_link': TARIFFS_LINK
        }
    )


def send_reset_password_message(user, confirm_link):
    send_template_mail(
        to=[user.email, ],
        subject='Скидання паролю',
        template='users/emails/reset_password.html',
        context={
            'user_name': user.first_name,
            'confirm_link': confirm_link
        }
    )


def send_new_subscription_message(user, subscription_link, start_date):
    send_template_mail(
        to=[user.email, ],
        subject='Ви підписалися на новий пакет послуг',
        template='payment_system/emails/new_subscription.html',
        context={
            'user_name': user.first_name,
            'subscription_link': subscription_link,
            'start_date': start_date
        }
    )


def send_invited_member_message(user, project_name, member):
    send_template_mail(
        to=[user.email, ],
        subject='Ви додали нового користувача до проєкту',
        template='payment_system/emails/invited_member.html',
        context={
            'user_name': user.first_name,
            'project_name': project_name,
            'member_full_name': member.get_full_name()
        }
    )


def send_confirm_membership_message(user, owner, project_name, confirm_link):
    send_template_mail(
        to=[user.email, ],
        subject='Вас запросили до нового проєкту',
        template='payment_system/emails/confirm_membership.html',
        context={
            'user_name': user.first_name,
            'owner_full_name': owner.get_full_name(),
            'project_name': project_name,
            'confirm_link': confirm_link
        }
    )


def send_project_token_message(user, link):
    send_template_mail(
        to=[user.email, ],
        subject='Доступ до токена',
        template='payment_system/emails/project_token.html',
        context={
            'user_name': user.first_name,
            'link': link
        }
    )


def send_membership_confirmed_message(user, member):
    send_template_mail(
        to=[user.email, ],
        subject='Користувач, якого Ви додали до проєкту, підтвердив ваше запрошення',
        template='payment_system/emails/membership_confirmed.html',
        context={
            'user_name': user.first_name,
            'member_full_name': member.get_full_name()
        }
    )


def send_removed_member_message(user, member, project_name):
    send_template_mail(
        to=[user.email, ],
        subject='Ви видалили користувача з проєкту',
        template='payment_system/emails/removed_member.html',
        context={
            'user_name': user.first_name,
            'member_full_name': member.get_full_name(),
            'project_name': project_name
        }
    )


def send_membership_removed_message(user, owner, project_name):
    send_template_mail(
        to=[user.email, ],
        subject='Вас видалили із проєкту',
        template='payment_system/emails/membership_removed.html',
        context={
            'user_name': user.first_name,
            'owner_full_name': owner.get_full_name(),
            'project_name': project_name
        }
    )


def send_new_invoice_message(user, invoice, invoice_link):
    send_template_mail(
        to=[user.email, ],
        subject='Новий рахунок',
        template='payment_system/emails/new_invoice.html',
        context={
            'user_name': user.first_name,
            'subscription_name': invoice.project_subscription.subscription,
            'start_date': invoice.project_subscription.start_date,
            'expiring_date': invoice.project_subscription.expiring_date,
            'invoice_link': invoice_link
        }
    )
