try:
    from django.conf.urls.defaults import *
except ImportError:
    from django.conf.urls import patterns, include

urlpatterns = patterns('',
    (r"^gen_url/", include('libthumbor.django.urls')),
)
