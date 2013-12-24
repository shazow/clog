from clog.model.meta import Session, BaseModel

from sqlalchemy import types, Column, Index, ForeignKey, PrimaryKeyConstraint
from datetime import datetime, timedelta
import time
import uuid

__all__ = [
    'Alias',
    'Entry',
    'random_id',
]


"""
The schema is designed in such a way that databases can be sync'd and merged
together with little effort and no collisions. That is, no incremental primary
keys that could get out of sync between databases.
"""


def random_id():
    return uuid.uuid1().get_bytes()


class Entry(BaseModel):
    """
    `session_id` is used to identify a collection of actions on one tag instance.
    for example, a sequence of work:start, work:stop, work:duration entries
    would all be placed under the same session_id. you can have many tags with
    the same tag name but different session_id's, as session_id's are only
    common within a collection.
    """
    __tablename__ = 'entry'

    id = Column(types.LargeBinary(16), default=random_id, nullable=False, primary_key=True)

    timestamp = Column(types.DateTime, default=datetime.now, nullable=False)

    tag = Column(types.String, nullable=False)  # food, sleep, workout, entity, alias, ...
    type = Column(types.String)  # start, stop, duration, pause, resume, note, tag, person, place, alias, ...
    value = Column(types.UnicodeText)  # Usually a label, notes, or some parsed value.

    session_id = Column(types.LargeBinary(16), default=random_id, nullable=False)


    def create_followup(self, **kw):
        return Entry.create(session_id=self.session_id, **kw)

    def __str__(self):
        tagname = self.tag
        if self.type:
            tagname += ':' + self.type
        timestamp = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        if self.type == 'duration':
            return "%s\t%s\t%s" % (timestamp, tagname, self.value and timedelta(seconds=int(self.value)))

        return "%s\t%s\t%s" % (timestamp, tagname, self.value or '')


Index('entry_idx',
      Entry.timestamp,
      Entry.tag,
      Entry.type,
      unique=True)

Index('entry_tag_idx',
      Entry.tag,
      Entry.timestamp)

Index('entry_session_idx',
      Entry.session_id,
      Entry.timestamp)


class Alias(BaseModel):
    """
    Local alias cache. This is computed on the fly as new alias Entry types are
    added.
    """
    __tablename__ = 'alias'

    tag = Column(types.String, nullable=False)
    value = Column(types.UnicodeText)
    entity_id = Column(types.LargeBinary(16), ForeignKey(Entry.id))

    __table_args__ = (
        PrimaryKeyConstraint('tag', 'value'),
        {}
    )
