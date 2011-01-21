"""SQLAlchemy Metadata and Session object"""
from sqlalchemy import MetaData, select, bindparam, types
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session as SessionBase
from sqlalchemy.interfaces import ConnectionProxy

from datetime import datetime, date
import time

__all__ = ['Session', 'metadata', 'BaseModel']

Session = scoped_session(sessionmaker(expire_on_commit=False))
metadata = MetaData()

convert_types = {
    types.LargeBinary: (
        lambda o: o.encode('hex'),
        lambda s: s.decode('hex')
    ),
    types.DateTime: (
        lambda o: o.strftime('%Y-%m-%d %H:%M:%S'),
        lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    ),
    types.Date: (
        lambda o: o.strftime('%Y-%m-%d'),
        lambda s: date.strptime(s, '%Y-%m-%d')
    ),
}

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

    def __export__(self):
        d = {}
        for col in self.__table__.columns:
            encode, decode = convert_types.get(col.type.__class__, (lambda v: v, lambda v: v))
            d[col.name] = encode(getattr(self, col.name))

        return d

    @classmethod
    def __import__(cls, d):
        params = {}
        for k, v in d.items():
            col = cls.__table__.columns.get(k)
            if col is None:
                continue

            encode, decode = convert_types.get(col.type.__class__, (lambda v: v, lambda v: v))
            params[str(k)] = decode(v)

        return cls.create(**params)


BaseModel = declarative_base(metadata=metadata, cls=_Base)
