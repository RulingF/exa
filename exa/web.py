# -*- coding: utf-8 -*-
'''
Web Application
==================================
Entry point for communication between Python and the standalone exa web
application (HTML/CSS/JS).
'''
import os
from tornado.web import Application, RequestHandler
from tornado.template import Loader
from tornado.ioloop import IOLoop
from jinja2 import Environment, FileSystemLoader
from exa import Config
from exa.utils import mkpath


def build_static_path_kwargs():
    '''
    '''
    kwargs = {}
    for root, subdirs, files in os.walk(Config.static):
        print(root)
        print(subdirs)
        print(files)
        splitdir = root.split(Config.static)[1]
        directory = 'static'
        if splitdir:
            directory = directory + splitdir
        for name in files:
            if name.endswith('js'):
                print(name)
                n = name.replace('.', '_')
                n = n.replace('-', '_')
                kwargs[n] = '\'' + '/'.join((directory.replace('\\', '/'), name)) + '\''
    return kwargs


templates_path = Config.templates
static_path = Config.static
kwargs = build_static_path_kwargs()


class HelloWorldHandler(RequestHandler):
    '''
    '''
    def get(self):
        self.write('Hello World')


class DashboardHandler(RequestHandler):
    '''
    '''
    def get(self):
        self.write(jinja2_loader.get_template('dashboard.html').render(**kwargs))

#class SessionHandler(RequestHandler):
#    '''
#    '''
#    def get(self):
#        self.write(jinja2_loader.get_template('dashboard.html').render(**kwargs))

#class RoutingHandler(RequestHandler):
#    '''
#    '''
#    def get(self):
#        self.write(jinja2_loader.get_template('routing.html'))


def serve(port=5000):
    '''
    '''
    app.listen(port)
    IOLoop.instance().start()


#print(Config.static)

tornado_settings = {
    'static_path': Config.static
}
tornado_handlers = [
    (r'/', DashboardHandler),
    (r'/hi', HelloWorldHandler),
    #(r'/routing', RoutingHandler),
    #(r'/#!/sessions', SessionHandler),
]
jinja2_loader = Environment(loader=FileSystemLoader(searchpath=templates_path))
app = Application(tornado_handlers, **tornado_settings)
