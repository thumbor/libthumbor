#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

'''Generic view for create thumbor encrypted urls.'''
import logging

from django.http import Http404, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponse
from django.conf import settings

from libthumbor.crypto import CryptoURL

THUMBOR_SECURITY_KEY = getattr(settings, 'THUMBOR_SECURITY_KEY', 'my-security-key')

def generate_url(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    crypto = CryptoURL(THUMBOR_SECURITY_KEY)
    
    try:
        args = request.GET
        # convert Django QueryDict to a python dict
        args = dict(zip(map(str, args.keys()), args.values()))

        if 'width' in args:
            args['width'] = int(args['width'])

        if 'height' in args:
            args['height'] = int(args['height'])

        if 'crop_top' in args or 'crop_left' in args or 'crop_right' in args or 'crop_bottom' in args:
            args['crop'] = ((int(args['crop_left']), int(args['crop_top'])),
                    (int(args['crop_right']), int(args['crop_bottom'])))
        
        return HttpResponse(crypto.generate(**args), mimetype="text/plain")
    except (ValueError, KeyError), e:
        logging.warning(str(e))
        return HttpResponseBadRequest()
