from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.orm import relationship

from model import Model


class User(Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    phone = Column(Text, nullable=False, unique=True)
    disconnection_date = Column(DateTime, default=datetime.now)
    memberships = relationship('Chat', secondary='membership', backref='User')

    def serialize(self):
        date = self.disconnection_date.strftime("%Y-%m-%d %H:%M:%S") if self.disconnection_date else None
        return {
            'name': self.name,
            'phone': self.phone,
            'disconnection_date': date
        }
