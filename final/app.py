from tornado import ioloop
from tornado.web import Application

from settings import PORT

from connection import Connection


if __name__ == "__main__":
    print('Welcome! listening on port {}'.format(PORT))

    Application([(r"/", Connection,)]).listen(PORT)
    ioloop.IOLoop.instance().start()
