from rest_framework.routers import DefaultRouter

from django.urls import path, include

from book.views import (
    BookApiView,
    PublisherApiView
)


router = DefaultRouter()
router.register('books', BookApiView)
router.register('publishers', PublisherApiView)

app_name = 'book'

urlpatterns = [
    path('', include(router.urls))
]
