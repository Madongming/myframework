#!/opt/python/bin/python3
# -*- coding: utf-8 -*-
 
__author__ = 'Cody Ma'

'''
Models
'''

from orm import Model, StringField, FloatField, TextField
import time, uuid

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = 'users'
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    groups = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)

class Group(Model):
    __table__ = 'groups'
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    permission_path = TextField()
    created_at = FloatField(default=time.time)
