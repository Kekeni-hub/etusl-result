from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import DeviceTokenSerializer
from .models import DeviceToken


class DeviceTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Register or update a device token for the authenticated user."""
        serializer = DeviceTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_value = serializer.validated_data['token']
        platform = serializer.validated_data.get('platform', 'other')
        metadata = serializer.validated_data.get('metadata')

        obj, created = DeviceToken.objects.update_or_create(
            token=token_value,
            defaults={'user': request.user, 'platform': platform, 'metadata': metadata}
        )

        return Response(DeviceTokenSerializer(obj).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request):
        """Unregister a device token. Accepts `token` in body or query."""
        token_value = request.data.get('token') or request.query_params.get('token')
        if not token_value:
            return Response({'detail': 'token required'}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = DeviceToken.objects.filter(token=token_value, user=request.user).delete()
        if deleted:
            return Response({'detail': 'deleted'}, status=status.HTTP_200_OK)
        return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)
