import requests
from django.conf import settings


def send_registration_email(email, first_name):
    header_obj = {
        "Content-Type": "application/json",
        "Authorization": f"Token {settings.POSTMAN_TOKEN}",
    }
    data_obj = {
        "recipient": email,
        # "template": "59_email_data_ocean_registration"
        "text": f"{first_name}, ви успішно зареєстровані у системі Data Ocean.\r\n Якщо Вами такі дії не проводились, проігноруйте цей лист.\r\n З повагою, Data Ocean",
        "subject": "Підтвердження реєстрації на Data Ocean"
    }
    response = requests.post(f"{settings.POSTMAN_URL}api/v1/email/", json=data_obj, headers=header_obj)
    print(f'Sending email status = {response.status_code}')


def send_plain_mail(email, subject, text):
    header_obj = {
        "Content-Type": "application/json",
        "Authorization": f"Token {settings.POSTMAN_TOKEN}",
    }
    data_obj = {
        "recipient": email,
        "text": text,
        "subject": subject,
    }
    response = requests.post(f"{settings.POSTMAN_URL}api/v1/email/", json=data_obj, headers=header_obj)
    return response.status_code
