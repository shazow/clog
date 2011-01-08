# Roadmap

## Step 1 (Complete?)

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

## Step 2.

Build a web frontend that visualizes data from your logs, with good import/export functionality.
