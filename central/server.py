from tornado import websocket
import tornado.ioloop
import json


PORT = 9000

clients = {}


class WebSocket(websocket.WebSocketHandler):

    def __init__(self, a, b, **kwargs):
        self.name = None
        super(WebSocket, self).__init__(a, b, **kwargs)

    def open(self):
        print("new connection!")

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        m = json.loads(message)

        if m['type'] == 'registry':
            self.handle_registry(m)

        if m['type'] == 'message':
            self.handle_message(m)

        if m['type'] == 'users':
            self.send_users_list()

    def on_close(self):
        print("{} closed his connection".format(self.name))
        if self.name in clients:
            del clients[self.name]
        self.send_users_list()

    def handle_registry(self, m):
        if m['value'] not in clients:
            self.name = m['value']
            clients[self.name] = self
        self.send_users_list()

    def handle_message(self, m):
        if m['to'] in clients:
            self.send_message(m['to'], m['value'])

    def broadcast(self, m):
        for name in clients:
            self.send_message(name, m['value'])

    def send_message(self, name, message):
        clients[name].write_message(json.dumps({'type': 'message', 'value': message, 'from': self.name}))
    
    def send_users_list(self):
        userslist = [name for name in clients.keys()]
        for name in clients:
            clients[name].write_message(json.dumps({'type': 'users', 'value': userslist}))


application = tornado.web.Application([(r"/", WebSocket,)])


if __name__ == "__main__":
    print('Welcome! listening on port {}'.format(PORT))

    application.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()
