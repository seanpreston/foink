import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from django import forms
from django.conf import settings
from django.contrib.auth import (
    authenticate,
    login,
)

from .models import Authority


class SendFoi(APIView):

    authentication_classes = settings.NO_CSRF_AUTH_CLASSES

    def post(self, request, *args, **kwargs):
        # subject = request.data['subject']
        content = request.data['emailContent']
        email_from = request.data['sender']
        authority_id = request.data['recipient']
        try:
            authority = Authority.objects.get(id=authority_id)
        except Authority.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response({"success": True}, status=status.HTTP_202_ACCEPTED)

        recipients = [
            'bianca@stotles.com',
            'sean@stotles.com',
            'taj@stotles.com',
        ]
        # if settings.ENV == settings.ENV_KEY_PROD:
        #     # Only send to actual people in production
        #     recipients = [authority.email]

        subject = "Freedom of Information Act - Request"
        message = Mail(
            from_email=email_from,
            to_emails=recipients,
            subject=subject,
            html_content=content,
        )
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)
        return Response(status=status.HTTP_202_ACCEPTED)


class AuthoritySearch(APIView):

    authentication_classes = settings.NO_CSRF_AUTH_CLASSES

    def post(self, request, *args, **kwargs):
        term = request.data.get('term', '')

        qs = Authority.objects.filter(name__icontains=term)[:20]
        results = []
        for authority in qs:
            results.append(authority.get_serialized())

        data = {
            'results': results,
            'paging_info': {
                'total_results': 20,
                'offset': 0,
                'limit': 20,
                'next_offset': 0,
            },
        }
        return Response(data, status=status.HTTP_202_ACCEPTED)
