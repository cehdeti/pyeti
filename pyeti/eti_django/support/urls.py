from django.urls import path

from . import views

urlpatterns = [
    path('support/', views.SupportView.as_view(), name='support'),
]
