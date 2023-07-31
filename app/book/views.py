from rest_framework import (
    viewsets,
    permissions,
    authentication,
    status
)
from rest_framework.response import Response
from book.serializers import (
    BookSerializer,
    PublisherSerializer,
    ReviewSerializer,
    BookSerializerOnlyView
)
from book.permissions import IsOwnerOrReadOnly, EveryoneCanAddReview
from core.models import (
    Book,
    Publisher
)

from rest_framework.decorators import action


class BookApiView(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        return self.queryset.all().order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return BookSerializerOnlyView
        elif self.action == 'retrieve':
            return BookSerializerOnlyView
        elif self.action == 'review_manage':
            permissions_obj = self.get_permissions()
            print(permissions_obj)
            return ReviewSerializer
        return BookSerializer

    @action(['GET', 'POST'], detail=True, url_path='review-manage', permission_classes=[EveryoneCanAddReview])
    def review_manage(self, request, pk=None):
        book = self.get_object()
        if request.method == 'GET':
            reviews = book.reviews.all()
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            reviews = request.data
            serializer = ReviewSerializer(data=reviews)
            if serializer.is_valid():
                reviews_obj = serializer.save(user=request.user)
                book.reviews.add(reviews_obj)
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


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
