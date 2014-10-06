from __future__ import unicode_literals

from django.conf.urls.defaults import url
from libthumbor.django.views import generate_url

urlpatterns = [
    url('^$', generate_url, name='thumbor_url'),
]
