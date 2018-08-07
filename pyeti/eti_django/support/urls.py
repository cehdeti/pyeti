from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'support/$', views.SupportView.as_view(), name='support'),
]
