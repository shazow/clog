*[Brainstorming branch for v2 of clog.]*

# clog

Captain's Log.

clog is a way to unite events we emit by hand with events emitted
programmatically by various services in our lives, allowing us to harness how
they relate to each other.

Think of it like a journal that you collaborate on with your computer.

Design goals:

1. Simple yet powerful data structure that can be easily implemented by many
   applications which will emit and consume these kinds of events to build a strong
   ecosystem.
2. Clog should be federated and encourage security-conscious storage and sharing
   by design.
3. Entries are immutable and stateless. Their keys depend on their contents, so
   they can't be modified in-place. Deletes could be handled by a plugin, but not
   part of the core design. If state is required for some functionality, it
   should be derived from the stream of stateless entries (and optionally
   maintained) by the app or plugin that needs it.
4. Plugins are completely optional. A node with zero plugins is still useful, as
   it can archive and possibly relay entries to another node that could do other
   things with them, like run plugins. Given a dump of entries, a plugin should
   aim to produce the same final state regardless of the dump's ordering. There
   is no guarantee which node will produce which entries and in which order
   they'll be relayed.


## Datastructure

Blobs of events, keyed by {timestamp, HASH}. HASH is the sha256 of the
concatenated values of {user, timestamp, session, type, action, value}.

    {
        user: [string],         // key of origin "person" entry [default: origin user]
        timestamp: [datetime],  // Timestamp of when the event was created [default: now]
        session: [string],      // (Optional) key of the origin entry
        type: [string],         // eat, sleep, exercise, alias, ...
        action: [string],       // (Optional) Modifier on type: start, stop, duration, pause, resume, note, tag, person, place, ...
        value: [string],        // A label, notes, or some parsed value
        metadata: [object],     // (Optional) user agent, debugging info, ... - not necessarily relayed
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


## Users & Sharing

Each clog database starts with an "origin" person entry. This is the default
user for this clog. It differs from other entries in that it does not have a
user field.

    {   // Key: 1234
        timestamp: 1421871634,
        type: "person"
    }

Users can have unlimited aliases that we refer to them by. This is purely for
our own convenience, it does not need to correlate to public identifiers.

    {
        user: "1234",
        type: "person",
        action: "alias",
        value: "shazow",
    }

We should also link social and cryptographic identities to users, perhaps import
from keybase.io or similar:

    {
        user: "1234",
        type: "person",
        action: "auth",
        value: "ssh-rsa AAAAB3Nz....bskD",
    }
    {
        user: "1234",
        type: "person",
        action: "twitter",
        value: "shazow",
    }

Now we can safely associate signed or Twitter messages to the correct person
entry, even if our internal alias differs.

A mention plugin can monitor @mentions and create corresponding person entries
for them if they don't exist, and track these mentions for future analysis (see
clog-plugin-mention example below).

Share mechanics can be implemented using a "share" or "assign" action, for example.


    {   // Key: AAAA
        user: "1234",
        type: "todo",
        value: "Give feedback on clog v2",
    },
    {
        user: "1234"
        session: "AAAA",
        type: "todo",
        action: "assign",
        value: "hyfen"
    }

A clog-plugin-share plugin might allow @hyfen to get access to the entire AAAA
session and synchronize state between @hyfen and @shazow. When plugins detect a
new person, they create a corresponding person with an alias to it.

    {   // Key: 2345
        user: "1234",
        type: "person",
    },
    {
        user: "1234",
        session: "2345",
        type: "person",
        action: "alias",
        value: "hyfen",
    }

Perhaps we've specified a remote for us to push events to for hyfen:

    {
        session: "AAAA"
        type: "person",
        action: "remote",
        value: "https://clog.hyfen.net",
    }

In this case, our clog could push events directly to @hyfen's database where
they will be held in a staging namespace until @hyfen chooses to adopt the
entries into his own database.

Later @hyfen might push back:

    {
        user: "2345"
        timestamp: 1421871634,
        session: "AAAA",
        type: "todo",
        action: "done",
    },
    {
        user: "2345"
        timestamp: 1421871634,
        session: "AAAA",
        type: "todo",
        action: "note",
        value: "Looks good!",
    }

We're hand-waving a lot of important auth negotiation details which might be
tricky to do with non-trusted parties. You could look at the established
auth/social links and have the other party authenticate against those. Every
send should be, of course, encrypted for the destination reader. Perhaps pushes
should only be allowed if an auth public key has been specified?

It's important to keep in mind that ultimately we're just passing around these
structured blobs. There is no obligation to merge them, or run them through any
specific plugin. It's up to you what you do with them.

Some plugins could require specific signing and database state to permit the
merging, or perhaps they keep a whitelist and piggyback on other credentials
(client cert or ssh keys?), or perhaps they just relay to another archival node
that deals with it.


## Commandline

A sketch of what a Unix-y command line tool suite might look like. It would make
just as much sense to have an all-in-one daemon running, but it's good to
imagine how the responsibilities might be broken up using command-line tools.

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


## Implementation thoughts

- Would be neat if the objects could be stored in a git-based database.
  - Otherwise, it could be stored in any ordered KV database, like LevelDB.
- JSON streams make it easy to build web clients and client-side plugins.
- What happens when two plugins conflict on emitted type namespaces? (Probably not important)
- Would be handy to have a clog-index which assists in generating an index for
  some value (e.g. for lookups of sessions, graph relationships, etc).

### clog-index

Not sure if this is a great idea, it would probably be better if plugins
maintained their own indices. But just for fun:

    $ clog-dump | clog-index --field=session session.idx
    Indexed 42 entries by session.

    $ clog-query session.idx "AAAA"
    ... [all entries in session AAAA, sorted logn lookup]

    $ clog-dump | clog-index person:mention --create mention.idx
    Indexed 123 person:mention entries, top instances:
    100   @foo
    20    @bar
    3     @baz

    $ clog-query mention.idx "@bar" --session tweet
    ... [all tweet entries that mention @bar, sorted logn lookup]

Commonly used clog indices would be defined in the config file such that they're
updated on the fly with clog-save. Plugins should be able to define their own
indices.


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
