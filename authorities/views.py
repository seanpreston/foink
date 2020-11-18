import json

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
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

from accounts.utils import CsrfExemptTokenAuth

from .models import Authority


class SearchFoi(APIView):

    authentication_classes = settings.NO_CSRF_AUTH_CLASSES

    def post(self, request, *args, **kwargs):
        authority_name = request.data['authority_name']
        term = request.data.get('term', '')

        results = [
            {
                "title": {
                    "text": "Low traffic neighbourhood correspondence",
                    "url": "https://www.whatdotheyknow.com/request/low_traffice_neighbourhood_corre_21#incoming-1670495"
                },
                "response_from": {
                    "text": "Redbridge Borough Council",
                    "url": "https://www.whatdotheyknow.com/body/redbridge_borough_council"
                },
                "response_to": {
                    "text": "Ben Rymer",
                    "url": "https://www.whatdotheyknow.com/user/ben_rymer"
                }
            }
        ]

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


class SendFoi(APIView):

    authentication_classes = (CsrfExemptTokenAuth, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            content = request.data['emailContent']
            email_from = request.data['sender']
            recipients = request.data['recipients']
        except (KeyError, IndexError):
            return Response(
                {"message": "emailContent, sender, recipients fields are all required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        split = content.split('\n')
        formatted = ""
        for segment in split:
            formatted += '<p>{}</p>'.format(segment)

        subject = "Freedom of Information Act - Request"

        recipient_emails = []
        failures = []
        for authority_id in recipients:
            try:
                authority = Authority.objects.get(id=authority_id)
            except Authority.DoesNotExist:
                failures.append(authority_id)
            else:
                # if settings.ENV == settings.ENV_KEY_PROD:
                #     # Only send to actual people in production
                #     recipient_emails.append(authority.email)
                pass

        recipient_emails = [
            'bianca@stotles.com',
            'sean@stotles.com',
            'taj@stotles.com',
        ]
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        for recipient in recipient_emails:
            message = Mail(
                from_email=email_from,
                to_emails=[recipient],
                subject=subject,
                html_content=formatted,
            )
            try:
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e.message)
                failures.append(authority_id)

        return Response({
            "success": True,
            "failures": failures,
        }, status=status.HTTP_202_ACCEPTED)


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
