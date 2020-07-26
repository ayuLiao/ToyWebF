from api import API
from middleware import Middleware

app = API()

@app.route("/home")
def home(request, response):
    response.text = "This is Home"

@app.route("/about")
def about(request, response):
    response.text = "This is about"

@app.route("/hello/{name}")
def hello(requst, response, name):
    response.text = f"Hello, {name}"

@app.route("/book")
class BooksResource(object):
    def get(self, req, resp):
        resp.text = "Books Page"

def handler1(req, resp):
    resp.text = "handler1"

def handler2(req, resp):
    resp.text = "handler2"

app.add_route("/handler1", handler1)
app.add_route("/handler2", handler2)

@app.route("/index")
def index(req, resp):
    template =  app.template("index.html", context={"name": "二两", "title": "ToyWebF"})
    # resp.body需要bytes，template方法返回的是unicode string，所以需要编码
    resp.body = template.encode()

def custom_exception_handler(request, response, exception_cls):
    response.text = "Oops! Something went wrong."

# 自定义错误
app.add_exception_handler(custom_exception_handler)

@app.route("/error")
def exception_throwing_handler(request, response):
    raise AssertionError("This handler should not be user")

class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("处理request", req.url)

    def process_response(self, req, resp):
        print("处理response", req.url)


class SimpleCustomMiddleware2(Middleware):
    def process_request(self, req):
        print("处理request2", req.url)

    def process_response(self, req, resp):
        print("处理response2", req.url)

app.add_middleware(SimpleCustomMiddleware)
app.add_middleware(SimpleCustomMiddleware2)
