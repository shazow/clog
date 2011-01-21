from clog.model.meta import Session, BaseModel
from clog.model import types as mytypes

from sqlalchemy import types, Column, Index, PrimaryKeyConstraint
from datetime import datetime, timedelta
import time
import uuid

__all__ = [
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
    tag_id is used to identify a collection of actions on one tag instance.
    For example, a sequence of work:start, work:stop, work:duration entries would
    all be placed under the same tag_id. You can have many tags with the same
    tag name but different tag_id's, as tag_id's are only common within a collection.
    """
    __tablename__ = 'entry'

    timestamp = Column(types.DateTime, default=datetime.now, nullable=False)

    tag = Column(types.String(128))
    tag_id = Column(types.LargeBinary(16), default=random_id, nullable=False)

    value = Column(types.UnicodeText)

    type = Column(mytypes.Enum(['start', 'stop', 'duration'], strict=False), nullable=True)

    def create_followup(self, **kw):
        return Entry.create(tag_id=self.tag_id, **kw)

    def __str__(self):
        tagname = self.tag
        if self.type:
            tagname += ':' + self.type
        timestamp = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        if self.type == 'duration':
            return "%s\t%s\t%s" % (timestamp, tagname, self.value and timedelta(seconds=int(self.value)))

        return "%s\t%s\t%s" % (timestamp, tagname, self.value or '')

    __table_args__ = (
        PrimaryKeyConstraint('timestamp', 'tag', 'type'),
        {}
    )

Index('entry_tag_idx',
      Entry.tag,
      Entry.timestamp)

Index('entry_tag_id_idx',
      Entry.tag_id,
      Entry.timestamp)
