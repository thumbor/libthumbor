from django.urls import path

from libthumbor.django.views import generate_url

urlpatterns = [  # pylint: disable=invalid-name
    path("gen_url/", generate_url, name="generate_thumbor_url"),
]
