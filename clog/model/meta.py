"""SQLAlchemy Metadata and Session object"""
from sqlalchemy import MetaData, select, bindparam
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session as SessionBase
from sqlalchemy.interfaces import ConnectionProxy

from datetime import datetime, date
import time

__all__ = ['Session', 'metadata', 'BaseModel']

Session = scoped_session(sessionmaker(expire_on_commit=False))
metadata = MetaData()

# Declarative base

from sqlalchemy.ext.declarative import declarative_base

class _Base(object):

    @classmethod
    def get(cls, id):
        return Session.query(cls).get(id)

    @classmethod
    def get_by(cls, **kw):
        return Session.query(cls).filter_by(**kw).first()

    @classmethod
    def get_or_create(cls, **kw):
        r = cls.get_by(**kw)
        if not r:
            r = cls(**kw)
            Session.add(r)

        return r

    @classmethod
    def create(cls, **kw):
        r = cls(**kw)
        Session.add(r)
        return r

    def delete(self):
        Session.delete(self)


    def __json__(self):
        return json.dumps(dict((n, getattr(self, n)) for n in self.__table__.c.keys() if n != 'id'), cls=SchemaEncoder)


BaseModel = declarative_base(metadata=metadata, cls=_Base)

import json

class SchemaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.__json__()
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        return json.JSONEncoder.default(self, obj)
