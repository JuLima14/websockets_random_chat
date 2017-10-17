from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from models.model import Model


class Message(Model):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chat.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    message = Column(Text)
    chat = relationship('Chat')
    user = relationship('User')
    date_created = Column(DateTime, default=datetime.now)

    def serialize(self):
        date = self.date_created.strftime("%Y-%m-%d %H:%M:%S") if self.date_created else None
        return {
            'from': self.user.serialize(),
            'date': date,
            'message': self.message
        }
