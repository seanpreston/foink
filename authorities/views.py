import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django import forms
from django.conf import settings
from django.contrib.auth import (
    authenticate,
    login,
)

from .models import Authority


class AuthoritySearch(APIView):

    authentication_classes = settings.NO_CSRF_AUTH_CLASSES

    def post(self, request, *args, **kwargs):
        data = json.dumps({})
        return Response(data, status=status.HTTP_202_ACCEPTED)
