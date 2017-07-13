from tornado import websocket
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import DB_CONNECTION, HISTORY_LENGTH

from database import Base, get_or_create

from models.user import User


engine = create_engine(DB_CONNECTION)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# new_user = User(name='new user')
# session.add(new_user)
# session.commit()


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


class Connection(websocket.WebSocketHandler):

    def __init__(self, a, b, **kwargs):
        self.user = None
        super(Connection, self).__init__(a, b, **kwargs)

    def open(self):
        print('new connection!')

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        m = json.loads(message)
        getattr(self, m['type'])(m)

    def on_close(self):
        print('{} closed his connection'.format(self.user.name))
        # Damn, do something

    def register(self, m):
        user_data = m['user']
        name, phone = user_data['name'], user_data['phone']

        # there is not an user with the given ID with an open connection
        if user_data['phone'] not in clients:
            self.user = get_or_create(session, User, name=name, phone=phone)
            clients[self.user.phone] = self
            print('{} is now online!'.format(self.user.name))
