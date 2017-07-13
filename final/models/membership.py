from sqlalchemy import Column, Integer, ForeignKey

from . import Base


class ChatMember(Base):
    __tablename__ = 'chat_member'
    chat_id = Column(Integer, ForeignKey('chat.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
