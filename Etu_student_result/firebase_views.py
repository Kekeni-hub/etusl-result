from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model, login
from django.conf import settings
from rest_framework.authtoken.models import Token

from .firebase_service import verify_id_token

User = get_user_model()


class FirebaseVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Verify a Firebase ID token sent from client and return user info and a DRF token.

        Body: { "id_token": "<firebase_id_token>", "create_session": true }
        - Returns: { uid, email, created, token }
        """
        id_token = request.data.get('id_token')
        create_session = bool(request.data.get('create_session', False))

        if not id_token:
            return Response({'detail': 'id_token required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded = verify_id_token(id_token)
        except Exception as e:
            return Response({'detail': f'Invalid token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # decoded contains uid, email, name, etc.
        uid = decoded.get('uid') or decoded.get('sub')
        email = decoded.get('email')
        name = decoded.get('name')

        if not uid:
            return Response({'detail': 'No uid in token'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create user by firebase uid stored in username to avoid collisions
        try:
            user, created = User.objects.get_or_create(username=uid, defaults={'email': email or '', 'first_name': name or ''})
        except Exception:
            # Fallback: try by email
            if email:
                user, created = User.objects.get_or_create(email=email, defaults={'username': uid, 'first_name': name or ''})
            else:
                return Response({'detail': 'Failed to create user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Ensure user is usable for auth
        if created:
            user.set_unusable_password()
            user.is_active = True
            user.save()

        # (Re)create DRF token for API authentication
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        # Optionally create a Django session (useful for web clients)
        if create_session:
            try:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
            except Exception:
                # Non-fatal; token-based auth still provided
                pass

        return Response({'uid': uid, 'email': user.email, 'created': created, 'token': token.key, 'decoded_token': decoded})
