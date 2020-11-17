from datetime import datetime

from rest_framework import (
    generics,
    status,
    serializers,
)
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings

from accounts.models import User
from accounts.utils import CsrfExemptTokenAuth

from .models import Note


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = (
            'uuid',
            'created_at',
            'modified_at',
            'text',
            'rating',
        )



class NotesView(generics.ListAPIView):

    serializer_class = NoteSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        qs = self.request.user.notes.all()
        start = self.request.query_params.get('start')
        if start:
            start = datetime.strptime(start, '%d-%m-%Y')
            qs = qs.filter(created_at__gte=start)

        end = self.request.query_params.get('end')
        if end:
            end = datetime.strptime(end, '%d-%m-%Y')
            qs = qs.filter(created_at__lt=end)

        rating = self.request.query_params.get('rating')
        if rating:
            qs = qs.filter(rating=rating)

        return qs


class NoteView(APIView):

    authentication_classes = (CsrfExemptTokenAuth, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, uuid, *args, **kwargs):
        note = request.user.notes.get(uuid=uuid)
        data = note.get_serialized()
        return Response(data, status=status.HTTP_202_ACCEPTED)

    def post(self, request, *args, **kwargs):
        text = request.data.get('text')
        rating = request.data.get('rating', 0)

        if not text:
            return Response(
                {'text': ['Please supply a valid email']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        note = Note.objects.create(
            text=text,
            author=request.user,
            rating=rating,
        )
        data = note.get_serialized()
        return Response(data, status=status.HTTP_201_CREATED)
