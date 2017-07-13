import json

from sqlalchemy import Column, ForeignKey, Integer, Text, and_, cast, DateTime
from sqlalchemy.orm import relationship

from . import Base, session
from message import Message


class Chat(Base):
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship('User')
    members = relationship('User', secondary='membership', backref='Chat')
    messages = relationship('Message', backref='sender')

    def send_history_to(self, connection):
        user = connection.user
        date = user.disconnection_date
        print 'user date: ', date
        messages = session.query(Message).filter(
            and_(
                Message.chat == self,
                Message.date_created >= date
            )
        )
        print messages
        connection.write_message(
            json.dumps(
                {
                    'type': 'messages_list',
                    'chat': self.name,
                    'messages': [
                        {
                            'from': message.user.name,
                            'date': message.date_created.strftime("%Y-%m-%d %H:%M:%S"),
                            'message': message.message
                        }
                        for message in messages
                    ]
                }
            )
        )

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
                            'chat': self.name,
                            'from': sender.name,
                            'date': new_message.date_created.strftime("%Y-%m-%d %H:%M:%S"),
                            'message': message
                        }
                    )
                )
