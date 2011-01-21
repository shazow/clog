import sys

import logging
log = logging.getLogger('clog')

from parsedatetime import parsedatetime, parsedatetime_consts
from datetime import datetime, timedelta

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
    # TODO: Refactor this into more sensible pieces.
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

    if options.pipe:
        value = sys.stdin.read()

    tag_id = model.random_id()

    if tag_type != 'duration':
        e = model.Entry.create(timestamp=when, tag=tag, tag_id=tag_id, type=tag_type, value=value and unicode(value))
        if tag_type == 'start' and options.pipe:
            tag_type = 'stop' # Trigger duration insert later
            when = datetime.now()
            e = model.Entry.create(timestamp=when, tag=tag, tag_id=tag_id, type=tag_type)
            Session.commit()

    else:
        # Create corresponding :start and :stop entries based on where `when` is completion time
        # and `value` is duration.

        # Normalize relative times
        now = datetime.now()
        when_stop = human_time_to_datetime(value)
        delta = when_stop - now
        when_stop = when + delta

        value = delta.seconds + delta.days*60*60*24 + 1

        e1 = model.Entry.create(timestamp=when, tag=tag, tag_id=tag_id, type='start')
        e2 = model.Entry.create(timestamp=when, tag=tag, tag_id=tag_id, type='duration', value=unicode(value))
        e3 = model.Entry.create(timestamp=when_stop, tag=tag, tag_id=tag_id, type='stop')

    if tag_type == 'stop':
        # Find the last 'start' tag of that type
        last_entry = Session.query(model.Entry).filter_by(tag=tag, type='start').order_by(model.Entry.timestamp.desc()).first()
        if last_entry:
            time_delta = when-last_entry.timestamp
            value = time_delta.seconds + time_delta.days*60*60*24
            e = model.Entry.create(timestamp=last_entry.timestamp, tag=tag, tag_id=last_entry.tag_id, type='duration', value=unicode(value))
            print "Duration recorded: %s" % timedelta(seconds=value)

    Session.commit()

def export_json_entries(options, args):
    q = Session.query(model.Entry)
    r = [e.__export__() for e in q]
    json.dump(r, sys.stdout)


def import_json_entries(options, args):
    o = json.load(sys.stdin)

    tag_id = model.random_id()
    for entry_dict in o:
        if 'tag_id' not in entry_dict:
            entry_dict['tag_id'] = tag_id.encode('hex')

        e = model.Entry.__import__(entry_dict)

        if tag_id and e.type == 'stop':
            tag_id = model.random_id()

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

    r = q.order_by(model.Entry.timestamp.desc()).all()
    if not r:
        print "No entries."
        return

    for entry in reversed(r):
        print entry
