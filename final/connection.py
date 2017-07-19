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
        print 'message: ', message
        try:
            m = json.loads(message)
            getattr(self, m['type'])(m)
        except Exception as e:
            print e

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

        self._send_state()

        print('{} is now online!'.format(self.user.phone))

    def create_chat(self, m):
        if not self.user: self.close()
        new_chat = get_or_create(
            session,
            Chat,
            dict(members=[self.user]),
            name=m['name'],
            owner=self.user
        )

        print '{} created a new chat: {}'.format(self.user.phone, new_chat.name)

    def add_member(self, m):
        if not self.user: self.close()
        new_member = session.query(User).filter_by(phone=m['phone']).first()
        chat = session.query(Chat).filter_by(name=m['chat']).first()
        chat.members.append(new_member)

        chat.notify_new_member(new_member, clients)

        session.commit()

    def send_message_to_chat(self, m):
        if not self.user: self.close()
        chat = session.query(Chat).filter_by(name=m['chat']).first()
        chat.send(m['message'], self, clients)

    def delete_chat(self, m):
        chat = session.query(Chat).filter_by(name=m['chat']).first()

        # Only the owner of a chat can delete it
        if chat.owner_id != self.user.id:
            self._send_error(
                'Only the chat owner is able to delete it'
            )
            return

        chat.notify_deleted(clients)

        chat.deleted = True
        session.commit()

    def remove_member(self, m):
        chat = session.query(Chat).filter_by(name=m['chat']).first()
        member = session.query(User).filter_by(phone=m['phone']).first()

        if chat.owner_id != self.user.id and self.user.id != member.id:
            self._send_error(
                'Only the chat owner is able to remove a member, or the member to himself'
            )
            return

        chat.notify_member_removed(member, clients)

        chat.members.remove(member)
        session.commit()

    def _send_state(self):
        self.write_message(
            json.dumps(
                {
                    'type': 'state',
                    'chats': [
                        chat.get_state_for(self.user)
                        for chat in self.user.memberships
                        if not chat.deleted
                    ]
                }
            )
        )

    def _send_error(self, detail):
        self.write_message(
            json.dumps(
                {
                    'type': 'error',
                    'detail': detail
                }
            )
        )
