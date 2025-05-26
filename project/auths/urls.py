from django.urls import path
from .views import CustomLoginView, logout_view


app_name = 'auths'

urlpatterns = [
    path('login', CustomLoginView.as_view(), name='login'),
    path('logout', logout_view, name='logout'),
]
