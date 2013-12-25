# Roadmap

## 1. Command-line Frontend (Complete)

* Build a simple command-line tool for logging things.

  ```
  Usage: clog [OPTIONS] TAG [VALUE]

  OPTIONS include:
  --timestamp TIME    Can be an ISO timestamp, or relative human time.
  ```

Each time you enter a clog, it generates a timestamped entry in the database.

* Tag hooks

  ```
  At 1am:
  $ clog sleep:start Feeling exhausted

  At 9am
  $ clog sleep:stop

  Hook generates entry equivalent of
  $ clog --timestamp "8 hours ago" sleep
  ```

## 2. Web Frontend (Not started)

Build a web frontend that visualizes data from your logs, with good import/export functionality.


## 3. Entity graphs (Not started)

* Track of relationships with people and objects through entities.

  ```
  $ clog entity:person batman
  $ clog entity:person Andrey Petrov
  $ clog entity:alias shazow -> Andrey Petrov
  ```

  An alias table will keep track of aliases for fast lookup of entities which
  are also stored as normal clog entries. An `entity:create` command will create
  an alias by default, too.

* Track attendance for locations.

  ```
  $ clog entity:place gym
  ...
  $ clog visit:start gym
  $ clog visit:with batman
  $ clog visit:with robin
  $ clog visit:stop
  ```

  Referencing an undefined entity will implicitly create it.

  Doing a :start type will implicitly create a session alias for that tag. When
  there are more than one aliases for some value, the latest is used.

  Amend to a previously stopped session:

  ```
  $ clog --session="gym" workout 20x5 squats
  ```

* Track expenses between parties and across sessions.

  ```
  $ clog expense:start Cabin trip
  $ clog expense:with batman
  $ clog expense:with robin
  $ clog expense:add batman $200 Food and drinks
  $ clog expense:add me $100 Gas
  $ clog expense:stop

  $ clog --session="Cabin trip" expense:balance
  Expenses recorded over 2 entries spanning 4 days: $300.00
  Average expense per person: $100.00

  Person | Session Balance
  -------+----------------
  me     |        +$100.00
  batman |           $0.00
  robin  |        -$100.00

  $ clog expense:balance
  Your outstanding balance with 1 other person: +$100.00

  Person |         Balance
  -------+----------------
  robin  |        -$100.00

  $ clog expense:move robin me $100
  $ clog expense:balance
  No outstanding balance.
  ```
