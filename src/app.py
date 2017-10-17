
import os
from tornado import ioloop
from tornado.web import Application

from settings import PORT

from connection import Connection


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print('Welcome! listening on port {}'.format(port))
    print('Welcome! listening on port {}'.format($PORT))
    Application([(r"/", Connection,)]).listen(port)
    ioloop.IOLoop.instance().start()
