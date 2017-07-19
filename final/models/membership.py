from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from model import Model


class Membership(Model):
    __tablename__ = 'membership'
    chat_id = Column(Integer, ForeignKey('chat.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    user = relationship('User')
    chat = relationship('Chat')
