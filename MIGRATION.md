# Migration

Migration your database to a new version that uses a new data format?

1. Install the version of clog which your database was created under (or simply don't install a schema-changing update just yet). Older versions should be tagged in github.
2. Dump your data using the ``--export-json`` flag, such as:

       clog --export-json > backup.json

3. Move your old database elsewhere.

       mv ~/.clog/db.sqlite ~/.clog/db.sqlite.bak

4. Upgrade your clog to the new version.

       pip install -U https://github.com/shazow/clog/tarball/master

5. Initialize a fresh database.

       clog

6. Import your dump.

       clog --import-json < backup.json

7. If everything worked as expected, you can delete your old database.

       rm ~/.clog/db.sqlite.bak
