from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r"^gen_url/", include('libthumbor.django.urls')),
)
