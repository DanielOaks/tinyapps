#!/usr/bin/env python3
# TinyApps - Database!
# written by Daniel Oaks <daniel@danieloaks.net>
# licensed under the BSD 2-clause license
import os
import sqlite3


class VersionedDb:
    """SQLite database that implements versioning and makes upgrading simple."""
    VERSION = None  # integer, 1 or up
    def __init__(self, path):
        """Load db and upgrade if necessary."""
        self._path = path

        # sanity check
        if self.VERSION is None:
            raise NotImplementedError('VERSION class variable must be an integer.')

        # create / open db
        if os.sep in self._path:
            folder = self._path.rsplit(os.sep, 1)[0]
            if not os.path.exists(folder):
                os.makedirs(folder)
        self._connection = sqlite3.connect(path)
        self._cursor = self._connection.cursor()

        # our data table is a simple key value store
        self._cursor.execute("CREATE TABLE IF NOT EXISTS vdb_data (key text, value text)")

        # get existing version
        db_version = self._get_db_version()
        if db_version is None:
            self.create_schema()
            db_version = self.VERSION

        # and upgrade as appropriate
        while db_version < self.VERSION:
            self.upgrade_schema()
            db_version = self._get_db_version()

    def save(self):
        """Save DB!"""
        self._connection.commit()

    def shutdown(self):
        """Close and shutdown."""
        self.save()
        self._connection.close()

    def _get_db_version(self):
        """Return db version or None if it doesn't exist."""
        self._cursor.execute("SELECT value FROM vdb_data WHERE key = ?", ('db_version',))
        row = self._cursor.fetchone()
        if row is None:
            db_version = None
        else:
            db_version = int(row[0])

        return db_version

    def _set_db_version(self, version):
        """Set db version."""
        version = int(version)
        self._cursor.execute("INSERT OR IGNORE INTO vdb_data (key, value) VALUES (?,?)", ('db_version', version))
        self._cursor.execute("UPDATE vdb_data SET value = ? WHERE key = ?", (version, 'db_version'))

    # to be overriden
    def create_schema(self):
        """Create schema if it doesn't already exist."""
        self._set_db_version(self.VERSION)

    def upgrade_schema(self, current_version):
        """Upgrade schema."""
        pass
