from tornado import websocket
import tornado.ioloop
import json


clients = {}


class SimpleWebSocket(websocket.WebSocketHandler):

    def __init__(self, a, b, **kwargs):
        self.name = None
        super(SimpleWebSocket, self).__init__(a, b, **kwargs)

    def open(self):
        print("Nuevo cliente!")

    def check_origin(self, origin):
        return True

    def on_message(self, message):        
        m = json.loads(message)

        if m['type'] == 'registry':
            if m['value'] not in clients:
                self.name = m['value']
                clients[m['value']] = self

        if m['type'] == 'message':
            for name in clients:
                self._send_message(name, m['value'])

        if m['type'] == 'users':
            self._send_users_list()
    
    def on_close(self):
        print("Cliente desconectado.")

        if self.name in clients:
            del clients[self.name]
    
    def _send_message(self, name, message):
        clients[name].write_message(json.dumps({'type': 'message', 'value': message}))
    
    def _send_users_list(self):
        userslist = [name for name in clients.keys()]
        for name in clients:
            clients[name].write_message(json.dumps({'type': 'users', 'value': userslist}))


application = tornado.web.Application([(r"/", SimpleWebSocket,)])


if __name__ == "__main__":
    application.listen(9000)
    tornado.ioloop.IOLoop.instance().start()

