from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.orm import relationship

from . import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    phone = Column(Text, nullable=False, unique=True)
    disconnection_date = Column(DateTime)
    memberships = relationship('Chat', secondary='membership', backref='User')
