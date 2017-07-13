from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from . import Base


class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chat.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    message = Column(Text)
    chat = relationship('Chat')
    user = relationship('User')
    date_created = Column(DateTime, default=datetime.now)
