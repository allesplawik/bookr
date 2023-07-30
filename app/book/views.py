from rest_framework import (
    viewsets,
    permissions,
    authentication
)
from rest_framework.response import Response
from book.serializers import (
    BookSerializer,
    PublisherSerializer
)
from book.permissions import IsOwnerOrReadOnly
from core.models import (
    Book,
    Publisher
)


class BookApiView(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        return self.queryset.all().order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublisherApiView(viewsets.ModelViewSet):
    serializer_class = PublisherSerializer
    queryset = Publisher.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        serializer = PublisherSerializer(data=data)
        if serializer.is_valid():
            publisher, created = Publisher.objects.get_or_create(user=user, **data)
            if not created:
                return Response({'message': 'Duplicated objec'}, status=404)
            return Response(data, status=201)
