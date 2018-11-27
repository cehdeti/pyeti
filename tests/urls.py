from django.conf.urls import url
from django.views.generic import View


urlpatterns = [
    url(r'^no-license/$', View.as_view(), name='no_license'),
    url(r'^expired-license/$', View.as_view(), name='expired_license'),
]
