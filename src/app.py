
import os
from tornado import ioloop
from tornado.web import Application

from settings import PORT

from connection import Connection


if __name__ == "__main__":
    port = int(os.environ.get("PORT", PORT))
    print('Welcome! listening on port {}'.format(port))
    Application([(r"/", Connection,)]).listen(port)
    tornado.ioloop.IOLoop.instance().start()
