import os
import inspect

# webob包包装WSGI的请求环境、相应状态、包头、http正文成请求对象和响应对象
from webob import Request, Response
from parse import parse
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise

from middleware import Middleware

class API(object):

    def __init__(self, templates_dir="templates", static_dir="static"):
        self.templates_dir = templates_dir
        self.static_dir = static_dir
        # url路由
        self.routes = {}
        # html文件夹
        self.templates_env = Environment(loader=FileSystemLoader(os.path.abspath(self.templates_dir)))
        # css、JavaScript文件夹
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)
        # 自定义错误
        self.exception_handler = None
        # 请求中间件，将api对象传入
        self.middleware = Middleware(self)

    def template(self, template_name, context=None):
        """返回模板内容"""
        if context is None:
            context = {}
        return self.templates_env.get_template(template_name).render(**context)

    # 不用webob只能直接返回二进制数据
    # def __call__(self, environ, start_response):
    #     response_body = b'Hello, World!'
    #     status = '200 OK'
    #     start_response(status, headers=[])
    #     return iter([response_body])


    def wsgi_app(self, environ, start_response):
        """通过 webob 将请求的环境信息转为request对象"""
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        path_info = environ["PATH_INFO"]
        static = "/" + self.static_dir
        # 以 /static 开头 或 中间件为空
        if path_info.startswith(static) or not self.middleware:
            # "/static/index.css" -> 只取 /index.css， /static开头只是用于判断
            environ["PATH_INFO"] = path_info[len(static):]
            return self.whitenoise(environ, start_response)
        return self.middleware(environ, start_response)


    def handle_request(self, request):
        """"""
        response = Response()
        handler, kwargs = self.find_handler(request.path)

        try:
            if handler is not None:
                if inspect.isclass(handler): # 如果是类，则获取其中的方法
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None: # 类中该方法不存在，则该类不支持该请求类型
                        raise AttributeError("Method now allowed", request.method)
                handler(request, response, **kwargs)
            else:
                self.defalut_response(response)
        except Exception as e:
            if self.exception_handler is None:
                raise  e
            else:
                # 自定义错误返回形式
                self.exception_handler(request, response, e)
        return response

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named
        return None, None

    def defalut_response(self, response):
        response.status_code = 404
        response.text = "Not Found"

    def route(self, path):

        def wrapper(handler):
            self.add_route(path, handler)
            return handler
        return wrapper

    def add_route(self, path, handler):
        # 相同路径不可重复添加
        assert path not in self.routes, "Such route already exists"
        self.routes[path] = handler

    def add_exception_handler(self, exception_handler):
        # 添加自定义error handler
        self.exception_handler = exception_handler

    def add_middleware(self, middleware_cls):
        # 添加中间件
        self.middleware.add(middleware_cls)


