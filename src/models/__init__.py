
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from chat import Chat
from user import User
from membership import Membership
from message import Message

Base = declarative_base()

engine = create_engine('sqlite:///database.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()



Base.metadata.create_all(engine, checkfirst=True)


def get_or_create(session, model, defaults, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
        for default in defaults:
            setattr(instance, default, defaults[default])
        session.add(instance)
        session.commit()
        return instance
    return instance
