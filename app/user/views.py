from rest_framework import (
    generics,
    permissions,
    authentication
)
from rest_framework.authtoken.views import ObtainAuthToken

from user.serializers import UserSerializer, TokenSerializer


class UserCreateApiView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserTokenApiView(ObtainAuthToken):
    serializer_class = TokenSerializer


class MeApiView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_object(self):

        return self.request.user
