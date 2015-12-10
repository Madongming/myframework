#!/opt/python/bin/python3
# -*- coding: utf-8 -*-
 
__author__ = 'Cody Ma'

'''
Cookies Of Handler
'''
import time, logging, hashlib, asyncio

from config import configs
from models import User

COOKIE_NAME = 'MyFrameWork'
_COOKIE_KEY = configs.session.secret

def user2cookie(user, max_age):
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return('-'.join(L))

@asyncio.coroutine
def cookie2user(cookie_str):
    if not cookie_str:
        return(None)
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return(None)
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return(None)
        user = yield from User.find(uid)
        if user is None:
            return(None)
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return(None)
        user.passwd = '******'
        return(user)
    except Exception as e:
        logging.exception(e)
        return(None)
