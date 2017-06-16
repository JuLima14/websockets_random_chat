from builtins import print
from tornado import websocket
import tornado.ioloop
import json


PORT = 9000
HISTORY_LENGTH = 10

clients = {}
chats = {}


class Service(object):
    @staticmethod
    def send_users_list():
        userslist = [name for name in clients.keys()]
        for name in clients:
            clients[name].write_message(
                json.dumps(dict(type='users', value=userslist))
            )

    @staticmethod
    def send_chats_list():
        chatslist = [name for name in chats.keys()]
        for name in clients:
            clients[name].write_message(
                json.dumps(dict(type='chats', value=chatslist))
            )

    @staticmethod
    def send_chat_history(client, chat):
        history = [dict(sender=m['sender'].name, message=m['message']) for m in chat.messages[-HISTORY_LENGTH:]]
        client.write_message(
            json.dumps(dict(type='history', value=history))
        )


class Chat(object):

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.members = [owner]
        self.messages = []

    def send(self, message, sender):
        self.messages.append(dict(message=message, sender=sender))
        for member in self.members:
            member.write_message(
                json.dumps(dict(type='message', value=message, sender=sender.name))
            )

    def add_member(self, member):
        self.members.append(member)

    def remove_member(self, member):
        self.members.remove(member)
        if not self.members:
            del chats[self.name]


class Member(websocket.WebSocketHandler):

    def __init__(self, a, b, **kwargs):
        self.name = None
        self.chats = []
        super(Member, self).__init__(a, b, **kwargs)

    def open(self):
        print("new connection!")

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        m = json.loads(message)
        getattr(self, m['type'])(m)

    def on_close(self):
        print("{} closed his connection".format(self.name))
        if self.name in clients:
            del clients[self.name]
        for chat in self.chats:
            chat.remove_member(self)
        Service.send_users_list()
        Service.send_chats_list()

    def register(self, m):
        if m['user'] not in clients:
            self.name = m['user']
            clients[self.name] = self
            print('{} is now online!'.format(self.name))
            Service.send_users_list()
            Service.send_chats_list()

    def create_chat(self, m):
        chats[m['name']] = Chat(m['name'], self)
        self.chats.append(chats[m['name']])
        Service.send_chats_list()

    def join_to_chat(self, m):
        chats[m['name']].add_member(self)
        self.chats.append(chats[m['name']])
        Service.send_chat_history(self, chats[m['name']])

    def send_message_to_chat(self, m):
        chats[m['name']].send(m['message'], self)


application = tornado.web.Application([(r"/", Member,)])


if __name__ == "__main__":
    print('Welcome! listening on port {}'.format(PORT))

    application.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()
