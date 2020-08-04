import hmac
import hashlib
import re
from datetime import timedelta
from rest_framework import generics, views
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings
from data_ocean.postman import send_plain_mail
from .models import DataOceanUser, CandidateUserModel
from .serializers import DataOceanUserSerializer, CustomRegisterSerializer, LandingMailSerializer


REGISTRATION_CONFIRM_SUBJECT = 'Підтвердження реєстрації на Data Ocean'
REGISTRATION_CONFIRM_MSG = (
    "{first_name}, ми отримали запит на реєстрацію у системі Data Ocean.\r\n"
    "Щоб підтвердити адресу Вашої електронної пошти, "
    "перейдіть за цим посиланням: \r\n{confirm_link}\r\n"
    "Якщо Вами ці дії не проводились, проігноруйте цей лист.\r\n"
    "З повагою, Data Ocean"
)


REGISTRATION_SUCCESS_SUBJECT = 'Ласкаво просимо у Data Ocean!'
REGISTRATION_SUCCESS_MSG = (
    "Дякуємо за реєстрацію у системі Data Ocean.\r\n"
    "Data Ocean — провайдер зручного доступу до відкритих даних.\r\n"
    "Ми розробляємо спеціальний сервіс, де Ви зможете "
    "отримати доступ до всіх важливих та існуючих регістрів, даних та звітностей.\r\n \r\n"
    "Якщо у Вас з'явились питання або пропозиції, зв'яжіться з нами info@dataocean.us. "
    "Будемо раді співпрацювати з Вами. Запевняємо, що наша співпраця буде плідною!\r\n"
    "З повагою, Data Ocean"
)


class UserListView(generics.ListAPIView):
    queryset = DataOceanUser.objects.all()
    serializer_class = DataOceanUserSerializer


class CustomRegisterView(views.APIView):
    permission_classes = (AllowAny, )

    def post(self, request: Request, *args, **kwargs):

        serializer = CustomRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # create a candidate variable, fill in the validated data
        user = CandidateUserModel(
            email=serializer.validated_data.get('email'),
            password=make_password(serializer.validated_data.get('password1')),  # hash
            first_name=serializer.validated_data.get('first_name'),
            last_name=serializer.validated_data.get('last_name'),
        )

        # check if this email is among existing users
        if DataOceanUser.objects.filter(email=user.email).exists():
            return Response({'detail': _('User with this email is already exists')}, status=400)

        # remove the candidate from CandidateUserModel, if exists (old ID is not used)
        CandidateUserModel.objects.filter(email=user.email).delete()

        # create a stamp of registration end time for this confirmation code
        user.expire_at = timezone.now() + timedelta(minutes=settings.CANDIDATE_EXPIRE_MINUTES)

        # generate a HMAC verification code
        msg = user.expire_at.strftime("%Y%m%dT%H%M%S%fZ") + user.email
        user.confirm_code = hmac.new(
            key=settings.SECRET_KEY.encode(),
            msg=msg.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        # add candidate to CandidateUserModel (with new ID)
        user.save()

        # create a letter to the candidate to confirm the email
        domain = re.sub(r'/$', '', settings.FRONTEND_SITE_URL)
        confirm_link = f'{domain}/auth/sign-up/confirmation/{user.id}/{user.confirm_code}/'
        message = REGISTRATION_CONFIRM_MSG.format(first_name=user.first_name, confirm_link=confirm_link)
        # send mail
        if settings.SEND_MAIL_BY_POSTMAN:
            # use POSTMAN
            send_status_code = send_plain_mail(user.email, REGISTRATION_CONFIRM_SUBJECT, message)
            if send_status_code != 201:
                return Response({'detail': _('Email not sent. Try again later.')}, status=503)
        else:
            # use EMAIL_BACKEND
            send_mail(
                subject=REGISTRATION_CONFIRM_SUBJECT,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=(user.email,),
                fail_silently=True,
            )

        return Response({
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }, status=200)


class CustomRegisterConfirmView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request, user_id: int, confirm_code: str, *args, **kwargs):

        # find user_id in the candidate table
        user = CandidateUserModel.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': _('Confirmation link is broken')}, status=400)

        # check that the confirmation code has expired
        if timezone.now() > user.expire_at:
            return Response({'detail': _('Confirmation link is expired.')}, status=400)

        # create an HMAC verification code and compare with the incoming one
        msg = user.expire_at.strftime("%Y%m%dT%H%M%S%fZ") + user.email
        confirm_code_check = hmac.new(
            key=settings.SECRET_KEY.encode(),
            msg=msg.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        # if the code does not match
        if confirm_code != confirm_code_check:
            return Response({'detail': _('Confirmation link is broken')}, status=400)

        # create a real user
        real_user = DataOceanUser.objects.create(
            email=user.email,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        # send mail
        if settings.SEND_MAIL_BY_POSTMAN:
            # use POSTMAN
            send_status_code = send_plain_mail(user.email, REGISTRATION_SUCCESS_SUBJECT, REGISTRATION_SUCCESS_MSG)
            if send_status_code != 201:
                return Response({'detail': _('Email not sent. Try again later.')}, status=400)
        else:
            # use EMAIL_BACKEND
            send_mail(
                subject=REGISTRATION_SUCCESS_SUBJECT,
                message=REGISTRATION_SUCCESS_MSG,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=(user.email,),
                fail_silently=True,
            )

        return Response(DataOceanUserSerializer(real_user).data, status=200)


class LandingMailView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request, *args, **kwargs):
        serializer = LandingMailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        name = serializer.validated_data.get('name')
        email = serializer.validated_data.get('email')
        subject = serializer.validated_data.get('subject')
        message = serializer.validated_data.get('message')

        # create a letter to the candidate to confirm the email
        msg = f'{name}, \r\n{email}, \r\n{message}'

        # send mail
        if not settings.SUPPORT_EMAIL:
            return Response({'detail': _('Email not sent. Try again later.')}, status=503)

        if settings.SEND_MAIL_BY_POSTMAN:
            # use POSTMAN
            send_status_code = send_plain_mail(settings.SUPPORT_EMAIL, subject, msg)
            if send_status_code != 201:
                return Response({'detail': _('Email not sent. Try again later.')}, status=503)
        else:
            # use EMAIL_BACKEND
            send_mail(
                subject=subject,
                message=msg,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=(settings.SUPPORT_EMAIL, ),
                fail_silently=True,
            )

        return Response({"email": email, }, status=200)
