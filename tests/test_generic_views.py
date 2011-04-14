#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

'''libthumbor generic views tests'''
import os

from libthumbor.crypto import CryptoURL

os.environ["DJANGO_SETTINGS_MODULE"] = 'testproj.settings'

try:
    from django.conf import settings
    from django.test import TestCase
    DJANGO_PRESENT = True
except ImportError:
    DJANGO_PRESENT = False

if DJANGO_PRESENT:

    class GenericViewsTestCase(TestCase):

        def test_without_url_param(self):
            response = self.client.get('/gen_url/')
            assert 404 == response.status_code, "Got %d" % response.status_code

        def test_generate_url_with_params_via_post(self):
            image_args = {'image_url': 'globo.com/media/img/my_image.jpg'}
            crypto = CryptoURL(settings.THUMBOR_SECURITY_KEY)

            response = self.client.post('/gen_url/', image_args)

            assert 200 == response.status_code, "Got %d" % response.status_code
            assert response.content == crypto.generate(**image_args)

        def test_generate_url_with_params_via_get(self):
            image_args = {'image_url': 'globo.com/media/img/my_image.jpg'}
            crypto = CryptoURL(settings.THUMBOR_SECURITY_KEY)

            response = self.client.get('/gen_url/?image_url=' + image_args['image_url'])

            assert 200 == response.status_code, "Got %d" % response.status_code
            assert response.content == crypto.generate(**image_args)

        def test_passing_invalid_aligns(self):
            image_args = {'image_url': 'globo.com/media/img/my_image.jpg', 'halign': 'sss'}

            response = self.client.post('/gen_url/', image_args)

            assert 404 == response.status_code, "Got %d" % response.status_code

        def test_passing_only_one_crop_value(self):
            image_args = {
                'image_url': 'globo.com/media/img/my_image.jpg',
                'crop_left': 100,
            }

            response = self.client.post('/gen_url/', image_args)

            assert 404 == response.status_code, "Got %d" % response.status_code

        def test_passing_only_one_crop_with_invalid_value(self):
            image_args = {
                'image_url': 'globo.com/media/img/my_image.jpg',
                'crop_top': 'bla',
            }

            response = self.client.post('/gen_url/', image_args)

            assert 404 == response.status_code, "Got %d" % response.status_code

        def test_passing_all_params(self):
            image_args = {
                'image_url': 'globo.com/media/img/my_image.jpg',
                'halign': 'left',
                'valign': 'middle',
                'meta': True,
                'smart': True,
                'width': 400,
                'height': 400,
                'flip': True,
                'flop': True
            }
            image_params = dict(image_args)
            image_params.update({
                'crop_top': 100,
                'crop_left': 100,
                'crop_bottom': 200,
                'crop_right': 200
            })
            image_args['crop'] = ((100,100),(200,200))

            crypto = CryptoURL(settings.THUMBOR_SECURITY_KEY)

            response = self.client.post('/gen_url/', image_params)

            assert 200 == response.status_code, "Got %d" % response.status_code
            assert response.content == crypto.generate(**image_args)
