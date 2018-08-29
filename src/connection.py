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
        try:
            m = json.loads(message)
            operation = m.pop('type')
            getattr(self, operation)(**m)
        except Exception as e:
            self._send_error(str(e))

    def on_close(self):
        self.user.disconnection_date = datetime.now()
        session.commit()
        del clients[self.user.email]
        print('{} closed his connection'.format(self.user.email))

    def register(self, user):
        name, email = user['name'], user['email']

        # Close previous connection if already logged in
        if email in clients:
            clients[email].close(409, 'You opened another session.')

        self.user = get_or_create(
            session,
            User,
            dict(name=name),
            email=email
        )

        clients[self.user.email] = self

        self._send_state()
        print('{} is now online!'.format(self.user.email))

    def create_chat(self, name):
        if not self.user: self.close()
        new_chat = get_or_create(
            session,
            Chat,
            dict(members=[self.user]),
            name=name,
            owner=self.user
        )
        print('{} created a new chat: {}'.format(self.user.phone, new_chat.name))

    def add_member(self, chat, phone):
        if not self.user: self.close()
        new_member = session.query(User).filter_by(phone=phone).first()

        if not new_member:
            self._send_error('User not found')
            return

        chat = session.query(Chat).filter_by(name=chat).first()
        chat.members.append(new_member)

        chat.notify_new_member(new_member, clients)
        session.commit()

    def send_message(self, chat, message):
        if not self.user: self.close()
        chat = session.query(Chat).filter_by(name=chat).first()
        chat.send(message, self, clients)

    def delete_chat(self, chat):
        chat = session.query(Chat).filter_by(name=chat).first()

        # Only the owner of a chat can delete it
        if chat.owner_id != self.user.id:
            self._send_error(
                'Only the chat owner is able to delete it'
            )
            return

        chat.notify_deleted(clients)

        chat.deleted = True
        session.commit()

    def remove_member(self, chat, phone):
        chat = session.query(Chat).filter_by(name=chat).first()
        member = session.query(User).filter_by(phone=phone).first()

        if chat.owner_id != self.user.id and self.user.id != member.id:
            self._send_error(
                'Only the chat owner is able to remove a member, or the member to himself'
            )
            return

        chat.notify_member_removed(member, clients)

        chat.members.remove(member)

        if not len(chat.members):
            chat.deleted = True

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
