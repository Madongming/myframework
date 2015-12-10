#!/opt/python/bin/python3
# -*- coding: utf-8 -*-
 
__author__ = 'Cody Ma'

'''
Error Url Handlers
'''

import asyncio

from aiohttp import web
from coroweb import get

@get('/400')
def http400(request):
    return({
        '__template__': '400.html'
    })

@get('/500')
def http500(request):
    return({
        '__template__': '500.html'
    })
