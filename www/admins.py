#!/opt/python/bin/python3
# -*- coding: utf-8 -*-
 
__author__ = 'Cody Ma'

'''
Url Handlers
'''

import re, time, json, logging, hashlib, base64, asyncio

from cookies import COOKIE_NAME, user2cookie, cookie2user
from aiohttp import web
from coroweb import get, post
from apis_Except import APIValueError, APIResourceNotFoundError, APIPermissionError
from models import User

@get('/mmadmin')
def admin(request):
    return({
        '__template__': 'admin.html'
    })
