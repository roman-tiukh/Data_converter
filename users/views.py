import hashlib
import hmac
import re
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils import timezone, translation
from django.utils.translation import ugettext_lazy as _
from rest_framework import generics, views
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from users import emails
from data_ocean.postman import send_plain_mail
from users.models import DataOceanUser, CandidateUserModel
from users.serializers import (
    DataOceanUserSerializer,
    CustomRegisterSerializer,
    LandingMailSerializer,
    QuestionSerializer,
    NotificationSerializer,
)


class UserListView(generics.ListAPIView):
    queryset = DataOceanUser.objects.all()
    serializer_class = DataOceanUserSerializer


class CustomRegistrationView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request, *args, **kwargs):
        user_language = translation.get_language()

        serializer = CustomRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # create a candidate variable, fill in the validated data
        user = CandidateUserModel(
            email=serializer.validated_data.get('email'),
            password=make_password(serializer.validated_data.get('password1')),  # hash
            first_name=serializer.validated_data.get('first_name'),
            last_name=serializer.validated_data.get('last_name'),
            language=user_language,
            phone=serializer.validated_data.get('phone', ''),
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
        emails.send_confirm_email_message(user, confirm_link)

        return Response({
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }, status=200)


class CustomRegistrationConfirmView(views.APIView):
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

        if DataOceanUser.objects.filter(email=user.email).exists():
            return Response({
                'detail': _('The link is invalid, the email address was confirmed earlier'),
            }, status=400)

        # create a real user
        real_user = DataOceanUser.objects.create(
            email=user.email,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
            language=user.language,
            phone=user.phone,
        )

        # send mail
        default_project = real_user.user_projects.get(is_default=True).project
        emails.send_registration_confirmed_message(real_user, default_project)
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
                recipient_list=(settings.SUPPORT_EMAIL,),
                fail_silently=True,
            )

        return Response({"email": email, }, status=200)


class RefreshTokenView(views.APIView):
    def get(self, request):
        token, created = Token.objects.get_or_create(user=request.user)
        token.delete()
        token = Token.objects.create(user=request.user)
        token.save()
        return Response({
            "token": token.key
        }, status=200)


class QuestionCreateView(generics.CreateAPIView):
    serializer_class = QuestionSerializer


class NotificationViewMixin:
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return self.request.user.notifications.order_by('is_read', '-created_at')


class NotificationListView(NotificationViewMixin, generics.GenericAPIView):
    def get(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({
            'alerts': request.user.get_alerts(),
            'messages': serializer.data,
        })


class NotificationReadView(NotificationViewMixin, generics.GenericAPIView):
    def put(self, request, pk):
        notification = self.get_object()
        notification.read()
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class NotificationReadAllView(NotificationViewMixin, generics.GenericAPIView):
    def put(self, request):
        for notification in self.get_queryset():
            notification.read()
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class NotificationDeleteView(NotificationViewMixin, generics.GenericAPIView):
    def delete(self, request, pk):
        notification = self.get_object()
        notification.delete()
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
