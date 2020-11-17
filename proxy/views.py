from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheck(APIView):

    def get(self, request, *args, **kwargs):
        # TODO: Actually check something
        return Response(status=status.HTTP_200_OK)
