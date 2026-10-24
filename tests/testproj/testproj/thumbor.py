from urllib.parse import urlsplit

from django.core.exceptions import PermissionDenied

from libthumbor.django.views import InvalidParameter


def validate_thumbor_url(request, options):
    if not request.user.is_authenticated:
        raise PermissionDenied
    image_url = options.get("image_url", "")
    if "://" not in image_url:
        image_url = f"http://{image_url}"
    if urlsplit(image_url).hostname != "images.example.com":
        raise InvalidParameter("Images must come from images.example.com.")
    if options.get("filters"):
        raise InvalidParameter("Filters are not allowed.")
