from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django import forms
from django.conf import settings
from django.contrib.auth import (
    authenticate,
    login,
)
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .models import User


class EmailSignUp(APIView):

    authentication_classes = settings.NO_CSRF_AUTH_CLASSES

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '')
        password = request.data.get('password')

        # try:
        #     validate_email(email)
        # except ValidationError:
        #     return Response(
        #         {'email': ['Please supply a valid email']},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        if not password:
            return Response(
                {'password': ['This field is required']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            account = User.objects.create(
                email=email,
                username=email,
            )
        except IntegrityError:
            return Response(
                {'email': ['An account with this email already exists']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        account.set_password(password)
        account.save()

        login(request, account)

        try:
            token = Token.objects.create(user=account)
        except IntegrityError:
            token = Token.objects.get(user=account)

        data = {
            'user': account.get_serialized(),
            'token': token.key,
        }
        return Response(data, status=status.HTTP_202_ACCEPTED)


class EmailSignIn(APIView):

    authentication_classes = settings.NO_CSRF_AUTH_CLASSES

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {'email': ['Please supply a valid email']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not password:
            return Response(
                {'password': ['This field is required']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = email.lower()
        account = authenticate(username=email, password=password)
        if not account:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        login(request, account)

        try:
            token = Token.objects.create(user=account)
        except IntegrityError:
            token = Token.objects.get(user=account)

        data = {
            'user': account.get_serialized(),
            'token': token.key,
        }
        return Response(data, status=status.HTTP_202_ACCEPTED)


class CustomUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("username", )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('index')
    template_name = 'signup.html'

    def form_valid(self, form):
        valid = super(SignUp, self).form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid
