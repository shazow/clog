from clog.model.meta import Session, BaseModel
from clog.model import types as mytypes

from sqlalchemy import orm, types, Column, Index, PrimaryKeyConstraint, ForeignKey
from datetime import datetime
import time

__all__ = [
    'Entry', 'Group',
]

class Group(BaseModel):
    __tablename__ = 'group'

    id = Column(types.Integer, primary_key=True) # Not used for data storage, just locality/sorting


class Entry(BaseModel):
    __tablename__ = 'entry'

    id = Column(types.Integer, primary_key=True) # Not used for data storage, just locality/sorting
    timestamp = Column(types.DateTime, default=datetime.now, nullable=False)

    tag = Column(types.String(128), index=True)
    value = Column(types.UnicodeText)

    type = Column(mytypes.Enum(['start', 'stop', 'duration'], strict=False), nullable=True)

    group_id = Column(types.Integer, ForeignKey(Group.id), nullable=False, index=True)
    group = orm.relationship(Group, backref='entries')

    def __str__(self):
        # TODO: Add human times in duration value
        tagname = self.tag
        if self.type:
            tagname += ':' + self.type
        timestamp = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return "%s\t%s\t%s" % (timestamp, tagname, self.value or '')

Index('entry_tag_idx',
      Entry.tag,
      Entry.timestamp)
