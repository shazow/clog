# clog

Brainstorming branch for v2 of clog.

## Storage

Blobs of events, keyed by {TIMESTAMP}-{HASH}. Hash is the hash of the
concatenated values of {timestamp, session, type, action, value}.

    {
        timestamp: [datetime],
        session: [string], // (Optional) key of the origin entry
        type: [string], // eat, sleep, exercise, alias, ...
        action: [string], // (Optional) Modifier on type: start, stop, duration, pause, resume, note, tag, person, place, ...
        value: [string], // A label, notes, or some parsed value
        metadata: [object], // (Optional) user agent, debugging info, ...
    }

Example:

    {   // Key: AAAA
        timestamp: 1421841034,
        type: "sleep",
        action: "start",
    },
    {   // Key: BBBB
        timestamp: 1421871634,
        session: "AAAA",
        type: "sleep",
        action: "stop",
    }

Plugins register handlers against some filter. For example, a Duration
plugin would register against the action="start" filter, and will be invoked
when the above entry is inserted. A plugin can emit new entries, such as:

    {
        timestamp: 1421871634,
        session: "AAAA",
        type: "sleep",
        action: "duration",
        value: "8h30m",
        metadata: {"agent": "github.com/shazow/clog-duration@3e2cb20"},
    }

Emitted events are stored in a separate bucket than natural events, and they're
not sync'd across clients by default. Each client may manage a separate set of
plugins which generate different sets of emitted events.

You could run an Archival node which runs resource-heavy plugins to analyze and
emit summary events. Device nodes can request specific event types to be sync'd
based on metadata filters. Device nodes could choose to maintain only a subset
of archival data, such as the last 30 days.


## Commandline

    $ clog sleep:start
    {
        ...
    }

    $ clog sleep:start | clog-save
    Saved AAAA: sleep:start

    $ clog sleep:stop | clog-plugin-duration | clog-save
    Saved AAAA/BBBB: sleep:stop
    -> Invoked duration (action=stop)
       -> Saved AAAA/CCCC: sleep:duration

The duration plugin detects a :duration entry and creates corresponding :start
and :stop entries under the AAAA session.

Ultimately, clog should know how to load plugins and save without having to put
it in the commandline:

    $ cat > ~/.clog/config << EOF
        plugin=duration
        autosave
    EOF

    $ clog --timestamp="today 11am" workout:duration 1 hour
    $ clog
    Saved DDDD: workout:duration
    -> Invoked duration (action=duration)
       -> Saved DDDD/EEEE: workout:start
       -> Saved DDDD/FFFF: workout:stop

This kind of mechanism makes it easy to programmatically generate events and
consume them from a script. For example, if you wanted to pipe all of your
tweets into clog, you could write an emitter:

    $ monitor-tweets shazow
    {
        timestamp: 1421871634,
        type: "tweet",
        value: "@hyfen What do you think of this clogging?",
        metadata: {
            "agent": "github.com/shazow/monitor-tweets@v1.0",
            "tweet": { [payload from Twitter API] },
        },
    },
    ... (streaming)

    $ monitor-tweets shazow | clog-save
    Saved GGGG: tweet
    ... (streaming)

We could write a plugin which extracts mentions and saves them as graph entity
entries.

    $ monitor-tweets shazow | clog-plugin-mention | clog-save
    Saved GGGG: tweet
    -> Invoked mention (type=tweet)
       -> Saved GGGG/FFFF: person:mention
    ... (streaming)


Backups and migrations would be easy:

    $ clog-dump --since "30 days ago" > backup.dump
    $ clog-save < backup.dump

Only missing entries will be loaded. We could also replay some amount of data
for a new plugin:

    $ clog-dump | clog-plugin-accounting | clog-save
    -> Invoked accounting (type=expense)
       -> Saved XXXX/YYYY: person:debt


## Recap of v1

### Basic

Track your eating:

    $ clog food Lunch: Chipotle

Track your sleep:

    $ clog sleep:start Feeling exhausted after shower.

    (Come back 8 hours later)
    $ clog sleep:stop
    $ clog
    2011-01-07 23:19:23	sleep:start	Feeling exhausted after shower.
    2011-01-08 07:19:29	sleep:stop	
    2011-01-07 23:19:23	sleep:duration	8:00:05

The `:duration` tag gets inserted automatically when a `:start` tag is closed with `:stop` tag.

### Retroactive

Forgot to log your 1 hour workout this morning? Insert duration retroactively:

    $ clog --timestamp="today 11am" workout:duration 1 hour
    $ clog
    2011-01-07 11:00:00	workout:start	
    2011-01-07 11:00:00	workout:duration	1:00:00
    2011-01-07 11:59:59	workout:stop

### Query

    $ clog --filter workout:duration
    2011-01-07 11:00:00	workout:duration	1:00:00
    2011-01-06 09:00:00	workout:duration	2:00:00
    2011-01-04 12:00:00	workout:duration	1:30:00

    $ clog --filter food
    2011-01-04 09:00:00	food	Breakfast: cereal
    2011-01-04 12:30:00	food	Lunch: Chipotle
    2011-01-04 18:00:00	food	Dinner: Fish
    2011-01-04 21:15:00	food	snack
    2011-01-05 12:30:00	food	Lunch: Subway
    2011-01-05 18:00:00	food	Dinner: Steak
    2011-01-06 11:00:00	food	Lunch: Indian
    2011-01-06 19:00:00	food	Dinner: Stew

### Full workflow

Use the ``clogflow`` script for a complete clog-based note-taking and time-tracking workflow, or make your own scripts.

    $ clogflow --help
    Usage: clogflow TAG [VALUE]

    Full :start to :stop workflow in a script.
    A :note is created per line, empty lines cause a :pause. <Ctrl-D> to finish

    $ clogflow work Clogging
    > Adding clogflow script
    > Testing clogflow
    > 
    (Paused)
    (Resumed)
    > Testing pausing, looks like it works.
    > ^D
    (Calculating duration)
    Duration recorded: 0:30:25.027582
    Duration includes 1 pauses spanning: 0:00:06.157021

    $ clog
    2011-01-20 23:07:08	work:start	Clogging
    2011-01-20 23:07:08	work:duration	0:30:25
    2011-01-20 23:12:17	work:note	Adding clogflow script
    2011-01-20 23:29:23	work:note	Testing clogflow
    2011-01-20 23:37:25	work:pause	
    2011-01-20 23:37:31	work:resume	
    2011-01-20 23:37:38	work:note	Testing pausing, looks like it works.
    2011-01-20 23:37:39	work:stop
