#!/opt/python/bin/python3
# -*- coding: utf-8 -*-
 
__author__ = 'Cody Ma'

'''
Application run
'''

import logging;
logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime
from aiohttp import web
from jinja2 import Environment, FileSystemLoader

import orm
from config import configs
from coroweb import add_routes, add_static
from handlers import cookie2user, COOKIE_NAME

def init_jinja2(app, **kw):
    logging.info('初始化jinja2....')
    options = dict(
        autoescape = kw.get('autoescape', True),
        block_start_string = kw.get('block_start_string', '{%'),
        block_end_string = kw.get('block_end_string', '%}'),
        variable_start_string = kw.get('variable_start_string', '{{'),
        variable_end_string = kw.get('variable_end_string', '}}'),
        auto_reload = kw.get('auto_reload', True)
    )
    path = kw.get('path', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
    logging.info('设置jinja2的模版路径为%s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name,func in filters.items():
            env.filters[name] = func
    app['__templating__'] = env

@asyncio.coroutine
def logger_factory(app, handler):
    @asyncio.coroutine
    def logger(request):
        logging.info('请求:% %' % (request.method, request.path))
        return(yield from handler(request))
    return(logger)

@asyncio.coroutine
def auth_factory(app, handler):
    @asyncio.coroutine
    def auth(request):
        logging.info('检查用户: %s %s' % (request.method, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)
        if cookie_str:
            user = yield from cookie2user(cookie_str)
            if user:
                logging.info('当前用户为: %s' % user.email)
                request.__user__ = user
        if yield from check_auth(user):
            return(web.HTTPFound('/signin'))
        return(yield from handler(request))
    return(auth)

@asyncio.coroutine
def data_factory(app, handler):
    @asyncio.coroutine
    def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = yield from request.json()
                logging.info('请求json: %s' % str(request.__data__))
            elif request.conten_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = yield from request.post()
                logging.info('请求form: %s' % str(request.__data__))
        return(yield from handler(request))
    return(parse_data)

@asyncio.coroutine
def response_factory(app, handler):
    @asyncio.coroutine
    def response(request):
        logging.info('响应处理程序...')
        r = yield from handler(request)
        if isinstance(r, web.StreamResponse):
            return(r)
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            response.content_type = 'application/octet-stream'
            return(resp)
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return(web.HTTPFound(r[9:]))
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return(resp)
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return(resp)
            else:
                r['__user__'] = request.__user__
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return(resp)
        if isinstance(r, int) and r >= 100 and r < 600:
            return(web.Response(r))
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return(web.Response(t, str(m)))
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return(resp)
    return(response)

def datetime_filter(t):
    t_before = int(time.time() - t)
    if t_before < 60:
        return(u'1分钟前')
    if t_before < 3600:
        return(u'%s分钟前' % (t_before // 60))
    if t_before < 86400:
        return(u'%s小时前' % (t_before // 3600))
    if t_before < 604800:
        return(u'%s天前' % (t_before // 86400))
    raw_date = datetime.fromtimestamp(t)
    return(u'%s年%s月%s日' % (raw_date.year, raw_date.month, raw_date.day))

@asyncio.coroutine
def init(loop):
    yield from orm.create_pool(loop=loop, **config.db)
    app = web.Application(loop=loop, middlewares=[
        logger_factory, auth_factory, response_factory
#        logger_factory, auth_factory, response_factory, data_factory 
    ])
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    add_routes(app, 'userregAlogin')
#用户添加访问逻辑
#    add_routes(app, 'handlers')
    add_static(app)
    srv = yield from loop.create_server(app.make_handler(), '0.0.0.0', 8888)
    logging.info('服务在http://192.168.1.53:8888开始运行...')
    return srv

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()
