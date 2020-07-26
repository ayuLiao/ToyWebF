from webob import Request

class Middleware(object):
    def __init__(self, app):
        self.app = app # API类实例

    def add(self, middleware_cls):
        # 实例化Middleware对象，包裹self.app
        self.app = middleware_cls(self.app)

    def process_request(self, req):
        # request前要做的处理
        pass

    def process_response(self, req, resp):
        # response后要做的处理
        pass

    def handle_request(self, request):
        self.process_request(request)
        response = self.app.handle_request(request)
        self.process_response(request, response)
        return response

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.app.handle_request(request)
        return response(environ, start_response)