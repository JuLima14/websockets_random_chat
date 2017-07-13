import json
from datetime import datetime

from tornado import websocket

from models import *


clients = {}


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
        self.user.disconnection_date = datetime.now()
        session.commit()
        del clients[self.user.phone]
        print('{} closed his connection'.format(self.user.phone))

    def register(self, m):
        user_data = m['user']
        name, phone = user_data['name'], user_data['phone']

        # Close previous connection if already logged in
        if phone in clients:
            clients[phone].close(409, 'You opened another session.')

        self.user = get_or_create(
            session,
            User,
            dict(name=name),
            phone=phone
        )

        clients[self.user.phone] = self

        self._send_chats_list()

        self._send_chats_history()

        print('{} is now online!'.format(self.user.phone))

    def create_chat(self, m):
        if not self.user: return
        new_chat = get_or_create(
            session,
            Chat,
            dict(members=[self.user]),
            name=m['name'],
            owner=self.user
        )

        print '{} created a new chat: {}'.format(self.user.phone, new_chat.name)

    def add_member(self, m):
        if not self.user: return
        new_member = session.query(User).filter_by(phone=m['phone']).first()
        chat = session.query(Chat).filter_by(name=m['chat']).first()
        chat.members.append(new_member)
        session.commit()

    def send_message_to_chat(self, m):
        if not self.user: return
        chat = session.query(Chat).filter_by(name=m['chat']).first()
        chat.send(m['message'], self, clients)

    def _send_chats_list(self):
        self.write_message(
            json.dumps(
                {
                    'type': 'chats_list',
                    'chats': [
                        {
                            'name': member_chat.name,
                            'members': [
                                {
                                    'name': member.name,
                                    'phone': member.phone
                                }
                                for member in member_chat.members
                            ]
                        }
                        for member_chat in self.user.memberships
                    ]
                }
            )
        )

    def _send_chats_history(self):
        for member_chat in self.user.memberships:
            member_chat.send_history_to(self)
