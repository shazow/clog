# clog

## Install

    pip install https://github.com/shazow/clog/tarball/master

Or

    easy_install https://github.com/shazow/clog/tarball/master


Upgrading to a newer version? Read the [migration notes](https://github.com/shazow/clog/blob/master/MIGRATION.md).


## Usage

    Usage: clog [OPTIONS] [TAG [VALUE]]

    Command Log. Or Captain's Log.


    Options:
      -h, --help            show this help message and exit
      --export-json         Export data into a list of JSON objects to STDOUT.
      --import-json         Import data from a list of JSON objects from STDIN.
      --filter=TAG          Filter clog entries by tag.
      -v, --verbose         Enable verbose output. Use twice to enable debug
                            output.

      TAG:
        --timestamp=TIMESTAMP
                            Date and time, absolute or relative human format.
                            Examples: 1985-11-30 12:00:00, 2pm, nov 30

## Examples

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
    Usage: /Users/shazow/env/clog/bin/clogflow TAG [VALUE]

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
