from flask.templating import render_template

__authors__ = ["shawkins", "Tsintsir", "sonph", "LeBat"]  # add yourself!

# internal (project libs)
from config import PORT_NUM, arg_parser
# base (python packages)
# external (pip packages)
from flask import Flask
import tornado.wsgi
import tornado.httpserver
import tornado.ioloop

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("hello.html")


@app.route('/my_var=<var>/')
def hello_var(var):
    return render_template("hello_var.html", var=var)

if __name__ == '__main__':
    # Parse arguments
    args = arg_parser.parse_args()
    # If we got a port_num config from args, override with that
    if args.port_num is not None:
        PORT_NUM = args.port_num

    # set up WSGI/tornado magic
    wsgi_container = tornado.wsgi.WSGIContainer(app)
    http_server = tornado.httpserver.HTTPServer(wsgi_container)
    http_server.listen(PORT_NUM)

    # this blocks the thread, don't do anything after this!
    tornado.ioloop.IOLoop.instance().start()
