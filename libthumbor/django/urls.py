try:
    from django.conf.urls.defaults import patterns, url
except ImportError:
    from django.conf.urls import patterns, url

urlpatterns = patterns(
    'libthumbor.django.views',
    url("^$", 'generate_url', name="generate_thumbor_url"),
)
