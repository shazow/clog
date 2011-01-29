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


def _tag(when, tag, tag_id=None, type=None, value=None):
    value = value and unicode(value)
    tag_id = tag_id or model.random_id()
    return model.Entry.create(timestamp=when, tag=tag, tag_id=tag_id, type=type, value=value and unicode(value))

def tag_start(when, tag, tag_id=None, type=None, value=None):
    return _tag(when=when, tag=tag, tag_id=tag_id, value=value, type='start')

def tag_stop(when, tag, tag_id=None, type=None, value=None):
    # FIXME: Rewrite this as one query
    last_start = Session.query(model.Entry).filter_by(tag=tag, type='start').order_by(model.Entry.timestamp.desc()).first()
    last_stop = Session.query(model.Entry).filter_by(tag=tag, type='stop').filter(model.Entry.timestamp > last_start.timestamp).first()
    if not last_start or last_stop:
        print "Couldn't find corresponding :start to end."
        return

    t = _tag(when=when, tag=tag, tag_id=last_start.tag_id, value=value, type='stop')

    time_delta = when - last_start.timestamp

    # Find all pause/resume types
    q = Session.query(model.Entry).filter_by(tag=tag).filter(model.Entry.type.in_(['pause', 'resume']))
    pauses = q.filter(model.Entry.timestamp > last_start.timestamp).order_by(model.Entry.timestamp.asc())

    pause_delta = timedelta()
    pause_count = 0
    last_time = None
    for p in pauses:
        if p.type == 'pause':
            last_time = p.timestamp
            pause_count += 1
        if p.type == 'resume' and last_time:
            pause_delta += (p.timestamp - last_time)
            last_time = None

    time_delta -= pause_delta
    value = time_delta.seconds + time_delta.days*60*60*24

    e = _tag(when=last_start.timestamp, tag=tag, tag_id=last_start.tag_id, value=value, type='duration')

    print "Duration recorded: %s" % time_delta
    if pause_count:
        print "Duration includes %d pauses spanning: %s" % (pause_count, pause_delta)


def tag_duration(when, tag, tag_id=None, type=None, value=None):
    now = datetime.now()
    when_stop = human_time_to_datetime(value)
    delta = when_stop - now
    when_stop = when + delta

    value = delta.seconds + delta.days*60*60*24 + 1

    e1 = _tag(timestamp=when, tag=tag, type='start')
    e2 = _tag(timestamp=when_stop, tag=tag, tag_id=e1.tag_id, type='stop')
    e3 = _tag(timestamp=when_stop, tag=tag, tag_id=e1.tag_id, value=value, type='duration')

    return e3

# FIXME: Get rid of repetitive code.

def tag_pause(when, tag, tag_id=None, type=None, value=None):
    last_start = Session.query(model.Entry).filter_by(tag=tag, type='start').order_by(model.Entry.timestamp.desc()).first()
    if not last_start:
        print "Could not find corresponding :start"

    return _tag(when=when, tag=tag, tag_id=last_start.tag_id, value=value, type='pause')

def tag_resume(when, tag, tag_id=None, type=None, value=None):
    last_start = Session.query(model.Entry).filter_by(tag=tag, type='start').order_by(model.Entry.timestamp.desc()).first()
    if not last_start:
        print "Could not find corresponding :start"

    return _tag(when=when, tag=tag, tag_id=last_start.tag_id, value=value, type='resume')

def tag_tag(when, tag, tag_id=None, type=None, value=None):
    last_start = Session.query(model.Entry).filter_by(tag=tag, type='start').order_by(model.Entry.timestamp.desc()).first()
    if not last_start:
        print "Could not find corresponding :start"

    # TODO: Add some sort of tag lookup table? Or a generic key-value metadata one?
    return _tag(when=when, tag=tag, tag_id=last_start.tag_id, value=value, type='tag')

def tag_note(when, tag, tag_id=None, type=None, value=None):
    last_start = Session.query(model.Entry).filter_by(tag=tag, type='start').order_by(model.Entry.timestamp.desc()).first()
    if not last_start:
        print "Could not find corresponding :start"

    return _tag(when=when, tag=tag, tag_id=tag_id, value=value, type='note')



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

    fn = {
        'start': tag_start,
        'stop': tag_stop,
        'duration': tag_duration,
        'pause': tag_pause,
        'resume': tag_resume,
        'note': tag_note,
        None: _tag,
    }

    fn[tag_type](when=when, tag=tag, tag_id=tag_id, value=value)

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
