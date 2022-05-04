from django.urls import path
from django.views.generic import View

urlpatterns = [
    path('no-license/', View.as_view(), name='no_license'),
    path('expired-license/', View.as_view(), name='expired_license'),
]
