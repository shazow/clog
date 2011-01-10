import sys

import logging
log = logging.getLogger(__name__)

from parsedatetime import parsedatetime, parsedatetime_consts
from datetime import datetime

from clog import model
Session = model.Session

try:
    import json
except ImportError, e:
    import simplejson as json

def human_time_to_datetime(s):
    const = parsedatetime_consts.Constants()
    cal = parsedatetime.Calendar(const)
    t, _ = cal.parse(s)
    return datetime(*t[:6])


def add_entry(options, args):
    when = datetime.now()
    if options.timestamp:
        when = human_time_to_datetime(options.timestamp)

    tag = args[0]
    tag_type = None

    if ':' in tag:
        tag, tag_type = tag.split(':', 1)

    value = None
    if len(args) > 1:
        value = ' '.join(args[1:])

    if tag_type == 'duration':
        # Create corresponding :start and :stop entries based on where `when` is completion time
        # and `value` is duration.

        # Normalize relative times
        now = datetime.now()
        when_stop = human_time_to_datetime(value)
        delta = when_stop - now
        when_stop = when + delta

        e1 = model.Entry.create(timestamp=when, tag=tag, type='start')
        e2 = model.Entry.create(timestamp=when, tag=tag, type='duration', value=unicode(delta.seconds))
        e3 = model.Entry.create(timestamp=when_stop, tag=tag, type='stop')
    else:
        e = model.Entry.create(timestamp=when, tag=tag, type=tag_type, value=value and unicode(value))

    if tag_type == 'stop':
        # Find the last 'start' tag of that type
        last_entry = Session.query(model.Entry).filter_by(tag=tag, type='start').order_by(model.Entry.id.desc()).first()
        if last_entry:
            time_delta = when-last_entry.timestamp
            model.Entry.create(timestamp=last_entry.timestamp, tag=tag, type='duration', value=unicode(time_delta.seconds))

    Session.commit()

def export_json_entries(options, args):
    q = Session.query(model.Entry)
    print "[",
    for i, entry in enumerate(q):
        if i>0:
            print ",",
        print entry.__json__(),
    print "]"

def import_json_entries(options, args):
    o = json.load(sys.stdin)

    for entry_dict in o:
        entry_dict = dict((str(k), v) for k,v in entry_dict.iteritems())
        entry_dict['timestamp'] = datetime.strptime(entry_dict['timestamp'], '%Y-%m-%d %H:%M:%S')
        model.Entry.create(**entry_dict)

    Session.commit()

def view_recent(options, args):
    q = Session.query(model.Entry)
    if options.filter:
        tag_name, tag_type = options.filter, None
        if ':' in tag_name:
            tag_name, tag_type = tag_name.split(':', 1)

        if tag_name:
            q = q.filter_by(tag=tag_name)

        if tag_type:
            q = q.filter_by(type=tag_type)

    r = q.order_by(model.Entry.id.desc()).limit(10).all()
    if not r:
        print "No entries."
        return

    for entry in reversed(r):
        print entry
