import hmac
import hashlib
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
from .serializers import DataOceanUserSerializer, CustomRegisterSerializer


class UserListView(generics.ListAPIView):
    queryset = DataOceanUser.objects.all()
    serializer_class = DataOceanUserSerializer


class CurrentUserProfileView(views.APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response(DataOceanUserSerializer(request.user).data, status=200)
        return Response(status=403)


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
        confirm_link = f'{settings.FRONTEND_SITE_URL}/api/custom/registration-confirm/{user.id}/{user.confirm_code}'
        subject = 'Підтвердження реєстрації на Data Ocean'
        text = f"{user.first_name}, ми отримали запит на реєстрацію у системі Data Ocean. Щоб підтвердити адресу Вашої електронної пошти, перейдіть за цим посиланням {confirm_link} \r\nЯкщо Вами ці дії не проводились, проігноруйте цей лист. \r\nЗ повагою, Data Ocean"
        # send mail
        if settings.SEND_MAIL_BY_POSTMAN:
            # use POSTMAN
            send_status_code = send_plain_mail(user.email, subject, text)
            if send_status_code != 201:
                return Response({'detail': _('Email not sent. Try again later.')}, status=400)
        else:
            # use EMAIL_BACKEND
            send_mail(subject, text, settings.DEFAULT_FROM_EMAIL, [user.email, ], fail_silently=True)

        return Response({"email": user.email, "first_name": user.first_name, "last_name": user.last_name}, status=200)


class CustomRegisterConfirmView(views.APIView):
    permission_classes = (AllowAny, )

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
        real_user = DataOceanUser(
            email=user.email,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        real_user.save()

        # create a greeting to the user
        subject = 'Ласкаво просимо у Data Ocean!'
        text = f"Дякуємо за реєстрацію у системі Data Ocean. \r\nData Ocean — провайдер зручного доступу до відкритих даних. Ми розробляємо спеціальний сервіс, де Ви зможете отримати доступ до всіх важливих та існуючих регістрів, даних та звітностей. \r\n \r\nЯкщо у Вас з'явились питання або пропозиції, зв'яжіться з нами info@dataocean.us. Будемо раді співпрацювати з Вами. Запевняємо, що наша співпраця буде плідною! \r\nЗ повагою, Data Ocean"
        # send mail
        if settings.SEND_MAIL_BY_POSTMAN:
            # use POSTMAN
            send_status_code = send_plain_mail(user.email, subject, text)
            if send_status_code != 201:
                return Response({'detail': _('Email not sent. Try again later.')}, status=400)
        else:
            # use EMAIL_BACKEND
            send_mail(subject, text, settings.DEFAULT_FROM_EMAIL, [user.email, ], fail_silently=True)

        return Response({
            "id": real_user.id,
            "email": real_user.email,
            "first_name": real_user.first_name,
            "last_name": real_user.last_name,
        }, status=200)
