from http.cookiejar import CookieJar
import json
import requests

from bs4 import BeautifulSoup
import mechanize
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

from .models import (
    Authority,
    FOIRequest,
)


class SearchFoi(APIView):

    authentication_classes = settings.NO_CSRF_AUTH_CLASSES

    def _get_browser(self):
        browser = mechanize.Browser()
        cookie_jar = CookieJar()
        browser.set_cookiejar(cookie_jar)
        browser.set_handle_robots(False)
        browser.addheaders = [
            (
                'User-agent',
                'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1',
            )
        ]
        return browser

    def post(self, request, *args, **kwargs):
        authority_name = request.data.get('authority_name', '')
        terms = request.data.get('terms', [])

        WDTK_BASE = 'https://www.whatdotheyknow.com'
        SEARCH_BASE_URL = WDTK_BASE + '/list/successful?utf8=%E2%9C%93'
        formatted_terms = authority_name + ' ' + '+'.join(terms)
        formatted_terms = formatted_terms.replace(" ", "%20")
        params = '&query={}&request_date_after=&request_date_before=&commit=Search'.format(formatted_terms)
        search_url = SEARCH_BASE_URL + params


        print("SEARCHING: " + search_url)
        browser = self._get_browser()
        res = browser.open(search_url)
        content = res.read()
        soup = BeautifulSoup(content)
        listings = soup.find_all("div", {"class": "request_listing"})

        results = []
        for listing in listings[:3]:
            links = listing.find_all("a", href=True)
            title = {
                "text": links[0].text,
                "url": WDTK_BASE + links[0]['href'],
            }
            response_from = {
                "text": links[1].text,
                "url": links[1]['href'],
            }
            response_to = {
                "text": links[2].text,
                "url": links[2]['href'],
            }
            results.append({
                "title": title,
                "response_from": response_from,
                "response_to": response_to,
            })

        # results = [
        #     {
        #         "title": {
        #             "text": "Low traffic neighbourhood correspondence",
        #             "url": "https://www.whatdotheyknow.com/request/low_traffice_neighbourhood_corre_21#incoming-1670495"
        #         },
        #         "response_from": {
        #             "text": "Redbridge Borough Council",
        #             "url": "https://www.whatdotheyknow.com/body/redbridge_borough_council"
        #         },
        #         "response_to": {
        #             "text": "Ben Rymer",
        #             "url": "https://www.whatdotheyknow.com/user/ben_rymer"
        #         }
        #     }
        # ]

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

        formatted = content.replace('\n', '<br>')
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
            else:
                try:
                    FOIRequest.objects.create(
                        text=formatted,
                        recipient=recipient,
                        sender=email_from
                    )
                except Exception:
                    pass

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
