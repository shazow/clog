# clog

## Install

    pip install https://github.com/shazow/clog/tarball/master

Or

    easy_install https://github.com/shazow/clog/tarball/master


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

Track your sleep:

    $ clog sleep:start Feeling exhausted after shower.

    (Come back 8 hours later)
    $ clog sleep:stop
    $ clog
    2011-01-07 23:19:23	sleep:start	Feeling exhausted after shower.
    2011-01-08 07:19:29	sleep:stop	
    2011-01-07 23:19:23	sleep:duration	28805

The :duration tag gets inserted automatically when a :start tag is closed with :stop tag.

Forgot to log your 1 hour workout this morning? Insert duration retroactively.

    $ clog --timestamp="today 11am" workout:duration 1 hour
    $ clog
    2011-01-07 11:00:00	workout:start	
    2011-01-07 11:00:00	workout:duration	3599
    2011-01-07 11:59:59	workout:stop

Query your clog

    $ clog --filter workout:duration
    2011-01-07 11:00:00	workout:duration	3599
    2011-01-06 09:00:00	workout:duration	7199
    2011-01-04 12:00:00	workout:duration	5399

    $ clog --filter food
    2011-01-04 09:00:00	food	Breakfast: cereal
    2011-01-04 12:30:00	food	Lunch: Chipotle
    2011-01-04 18:00:00	food	Dinner: Fish
    2011-01-04 21:15:00	food	snack
    2011-01-05 12:30:00	food	Lunch: Subway
    2011-01-05 18:00:00	food	Dinner: Steak
    2011-01-06 11:00:00	food	Lunch: Indian
    2011-01-06 19:00:00	food	Dinner: Stew


## Roadmap

### Step 1 (Complete)

* Build a simple command-line tool for logging things.

      Usage: clog [OPTIONS] TAG [VALUE]

      OPTIONS include:
      --timestamp TIME    Can be an ISO timestamp, or relative human time.

Each time you enter a clog, it generates a timestamped entry in the database.

* Tag hooks

      At 1am:
      $ clog sleep:start Feeling exhausted

      At 9am
      $ clog sleep:stop

      Hook generates entry equivalent of
      $ clog --timestamp "8 hours ago" sleep

### Step 2.

Build a web frontend that visualizes data from your logs, with good import/export functionality.
