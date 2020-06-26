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

from postman import send_plain_mail
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

        # отримати і перевірити дані
        serializer = CustomRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # створити змінну кандидата, заповнити провалідованими даними
        user = CandidateUserModel(
            email=serializer.validated_data.get('email'),
            password=make_password(serializer.validated_data.get('password1')),  # hash
            first_name=serializer.validated_data.get('first_name'),
            last_name=serializer.validated_data.get('last_name'),
        )

        # перевірити, чи є цей email серед існуючих користувачів
        if DataOceanUser.objects.filter(email=user.email).exists():
            return Response({'detail': _('User with this email is already exists')}, status=400)

        # видалити кандидата з CandidateUserModel, якщо існує (щоб не використовувався старий ID)
        CandidateUserModel.objects.filter(email=user.email).delete()

        # створити мітку часу закінчення дії реєстрації з цим кодом підтвердження
        user.expire_at = timezone.now() + timedelta(minutes=settings.CANDIDATE_EXPIRE_MINUTES)

        # створити код підтвердження за HMAC
        msg = user.expire_at.strftime("%Y%m%dT%H%M%S%fZ") + user.email
        user.confirm_code = hmac.new(
            key=settings.SECRET_KEY.encode(),
            msg=msg.encode('utf-8'),
            digestmod=hashlib.sha256  # md5
        ).hexdigest()

        # додати кандидата в CandidateUserModel (з новим ID)
        user.save()

        # створити лист кандидату для підтвердження email
        confirm_link = f'{settings.FRONTEND_SITE_URL}/api/custom/registration-confirm/{user.id}/{user.confirm_code}'
        subject = 'Підтвердження реєстрації на Data Ocean'
        text = f"Вітаємо, {user.first_name}! \r\nВи реєструєтесь у системі Data Ocean. \r\nПосилання на підтвердження: {confirm_link} \r\nЯкщо Вами ці дії не проводились, проігноруйте цей лист."
        # відправити лист
        if settings.SEND_MAIL_BY_POSTMAN:
            # з використанням POSTMAN
            send_status_code = send_plain_mail(user.email, subject, text)
            if send_status_code != 201:
                return Response({'detail': _('Email not sent. Try again later.')}, status=400)
        else:
            # з використанням EMAIL_BACKEND
            send_mail(subject, text, settings.DEFAULT_FROM_EMAIL, [user.email, ], fail_silently=True)

        return Response({"email": user.email, "first_name": user.first_name, "last_name": user.last_name}, status=200)


class CustomRegisterConfirmView(views.APIView):
    permission_classes = (AllowAny, )

    def post(self, request: Request, user_id: int, confirm_code: str, *args, **kwargs):

        # знайти user_id в таблиці кандидатів
        user = CandidateUserModel.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': _('Confirmation link is broken')}, status=400)

        # перевірити, чи не закіінчився строк дії кода підтвердження
        if timezone.now() > user.expire_at:
            return Response({'detail': _('Confirmation link is expired.')}, status=400)

        # створити код підтвердження за HMAC і порівняти із вхідним
        msg = user.expire_at.strftime("%Y%m%dT%H%M%S%fZ") + user.email
        confirm_code_check = hmac.new(
            key=settings.SECRET_KEY.encode(),
            msg=msg.encode('utf-8'),
            digestmod=hashlib.sha256  # md5
        ).hexdigest()

        # якщо код не співпадає
        if confirm_code != confirm_code_check:
            return Response({'detail': _('Confirmation link is broken')}, status=400)

        # створити реального користувача
        real_user = DataOceanUser(
            email=user.email,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        real_user.save()

        # створити лист користувачу з привітанням
        subject = 'Ласкаво просимо у Data Ocean!'
        text = f"Дякуємо за реєстрацію у системі Data Ocean. \r\nData Ocean — провайдер зручного доступу до відкритих даних. Ми розробляємо спеціальний сервіс, де Ви зможете отримати доступ до всіх важливих та існуючих регістрів, даних та звітностей. \r\n \r\nЯкщо у Вас з'явились питання або пропозиції, зв'яжіться з нами info@dataocean.us. Будемо раді співпрацювати з Вами. Запевняємо, що наша співпраця буде плідною! \r\nЗ повагою, Data Ocean"
        # відправити лист
        if settings.SEND_MAIL_BY_POSTMAN:
            # з використанням POSTMAN
            send_status_code = send_plain_mail(user.email, subject, text)
            if send_status_code != 201:
                return Response({'detail': _('Email not sent. Try again later.')}, status=400)
        else:
            # з використанням EMAIL_BACKEND
            send_mail(subject, text, settings.DEFAULT_FROM_EMAIL, [user.email, ], fail_silently=True)

        return Response({
            "id": real_user.id,
            "email": real_user.email,
            "first_name": real_user.first_name,
            "last_name": real_user.last_name,
        }, status=200)
