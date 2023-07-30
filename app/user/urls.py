from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.UserCreateApiView.as_view(), name='create'),
    path('token/', views.UserTokenApiView.as_view(), name='token'),
    path('me/', views.MeApiView.as_view(), name='me')
]
