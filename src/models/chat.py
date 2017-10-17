import json

from sqlalchemy import Column, ForeignKey, Integer, Text, and_, Boolean
from sqlalchemy.orm import relationship

from . import session

from models.model import Model

from message import Message


class Chat(Model):
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship('User')
    members = relationship('User', secondary='membership', backref='Chat')
    messages = relationship('Message', backref='sender')
    deleted = Column(Boolean, nullable=False, default=False)

    def serialize(self):
        return {
            'name': self.name,
            'owner': self.owner.serialize(),
            'members': [member.serialize() for member in self.members]
        }

    def get_state_for(self, user):
        date = user.disconnection_date

        messages = session.query(Message).filter(
            and_(
                Message.chat == self,
                Message.date_created >= date
            )
        )

        return {
            "chat": self.serialize(),
            "messages": [
                message.serialize()
                for message in messages
            ]
        }

    def send(self, message, connection, clients):
        sender = connection.user

        new_message = Message(message=message, chat=self, user=sender)
        session.add(new_message)
        self.messages.append(new_message)

        session.commit()

        for member in self.members:
            # If online, send.
            # Otherwise, it will be sent when he logs in
            if member.phone in clients:
                clients[member.phone].write_message(
                    json.dumps(
                        {
                            'type': 'message',
                            'chat': self.serialize(),
                            'from': sender.serialize(),
                            'date': new_message.date_created.strftime("%Y-%m-%d %H:%M:%S"),
                            'message': message
                        }
                    )
                )

    def notify_new_member(self, user, clients):
        for member in self.members:
            if member.phone in clients:
                clients[member.phone].write_message(
                    json.dumps(
                        {
                            'type': 'new_member',
                            'chat': self.serialize(),
                            'user': user.serialize()
                        }
                    )
                )

    def notify_deleted(self, clients):
        for member in self.members:
            if member.phone in clients:
                clients[member.phone].write_message(
                    json.dumps(
                        {
                            'type': 'chat_deleted',
                            'chat': self.serialize()
                        }
                    )
                )

    def notify_member_removed(self, user, clients):
        for member in self.members:
            if member.phone in clients:
                clients[member.phone].write_message(
                    json.dumps(
                        {
                            'type': 'member_removed',
                            'chat': self.serialize(),
                            'user': user.serialize()
                        }
                    )
                )
