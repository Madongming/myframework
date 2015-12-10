#!/opt/python/bin/python3
# -*- coding: utf-8 -*-
 
__author__ = 'Cody Ma'

'''
Api's Except Define
'''

class APIError(Exception):
    '''
        基本的APIError，包括error（必须）、data（可选）、message（可选）。
    '''
    def __init__(self, error, data='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message

class APIValueError(APIError):
    '''
    表明输入的值有错误或者无效。指定输入表单数据的错误字段。
    '''
    def __init__(self, field, message=''):
        super(APIValueError, self).__init__('value:invalid', field, message)

class APIResourceNotFoundError(APIError):
    '''
    表明资源没有找到。数据指定的资源名。
    '''
    def __init__(self, field, message=''):
        super(APIResourceNotFoundError, self).__init__('value:notfound', field, message)

class APIPermissionError(APIError):
    '''
    表明该api没有权限
    '''
    def __init__(self, message=''):
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)
