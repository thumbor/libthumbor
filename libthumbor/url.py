#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# https://github.com/heynemann/libthumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

'''URL composer to create options-based URLs for thumbor encryption.'''

import hashlib

def url_for(**options):
    '''Returns the url for the specified options'''

    if 'image_url' not in options:
        raise RuntimeError('The image_url argument is mandatory.')
    
    image_hash = hashlib.md5(options['image_url']).hexdigest()

    return image_hash
