from clog.model.meta import Session, BaseModel
from clog.model import types as mytypes

from sqlalchemy import types, Column, Index, PrimaryKeyConstraint
from datetime import datetime
import time

__all__ = [
    'Entry',
]

class Entry(BaseModel):
    __tablename__ = 'entry'

    id = Column(types.Integer, primary_key=True) # Not used for data storage, just locality/sorting
    timestamp = Column(types.DateTime, default=datetime.now, nullable=False)

    tag = Column(types.String(128), index=True)
    value = Column(types.UnicodeText)

    type = Column(mytypes.Enum(['start', 'stop', 'duration'], strict=False), nullable=True)

    def __str__(self):
        tagname = self.tag
        if self.type:
            tagname += ':' + self.type
        timestamp = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return "{0}\t{1}\t{2}".format(timestamp, tagname, self.value or '')

Index('entry_tag_idx',
      Entry.tag,
      Entry.timestamp)
