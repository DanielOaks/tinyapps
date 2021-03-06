#!/usr/bin/env python3
# TinyApps - User Store
# written by Daniel Oaks <daniel@danieloaks.net>
# licensed under the BSD 2-clause license
import datetime
import string

import passlib.utils
from passlib.hash import pbkdf2_sha512

from .db import VersionedDb


class TinyUsers(VersionedDb):
    """Manages users for a TinyApps instance."""
    VERSION = 1

    def __init__(self, path):
        super().__init__(path)

    def create_schema(self):
        super().create_schema()
        # urgh, we have the salt here just to have it all in a single db
        self._cursor.execute("CREATE TABLE IF NOT EXISTS site (salt BLOB)")
        self._cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, is_site_admin BOOLEAN, pepper BLOB, pw_hash TEXT)")
        self._cursor.execute("CREATE TABLE IF NOT EXISTS sessions (session_id TEXT, user_id INTEGER, expiry_ts INTEGER)")

    # user stuff
    def create_session(self, user_id=None, user_name=None):
        """Create a session for the given user"""
        user_info = self.user_info(user_id=user_id, user_name=user_name)

        # make sure they supplied valid creds
        if user_info is None:
            return None

        # create id
        session_id = passlib.utils.generate_password(size=50, charset=string.ascii_letters + string.digits)
        expiry_ts = datetime.datetime.now(datetime.timezone.utc).timestamp() + datetime.timedelta(weeks=4).total_seconds()

        # put into db
        self._cursor.execute("INSERT INTO 'sessions' (session_id, user_id, expiry_ts) VALUES (?, ?, ?)", (session_id, user_info['id'], expiry_ts))

        return session_id

    def user_info_from_session(self, session_id):
        """Given Session ID, return user info. If expired, delete session."""
        # make sure session exists
        self._cursor.execute("SELECT user_id, expiry_ts FROM 'sessions' WHERE session_id = ?", (session_id,))
        row = self._cursor.fetchone()
        if row is None:
            return None
        user_id, expiry_ts = row

        # see if session is expired
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        if expiry_ts < now_ts:
            return None

        return self.user_info(user_id=user_id)

    def user_info(self, user_id=None, user_name=None):
        """Return user info from given value."""
        # selection based on given cred
        if user_id is not None:
            self._cursor.execute("SELECT id, name, is_site_admin FROM 'users' WHERE id = ?", (user_id,))
        elif user_name is not None:
            self._cursor.execute("SELECT id, name, is_site_admin FROM 'users' WHERE name = ?", (user_name,))
        else:
            raise AttributeError('You must supply either user_name or user_id to retrieve user info')

        # make sure exists
        info_row = self._cursor.fetchone()
        if not info_row:
            return None

        # return real info dict
        user_id, name, is_site_admin = info_row
        info = {
            'id': user_id,
            'name': name,
            'is_site_admin': is_site_admin,
        }

        return info

    # auth
    @property
    def site_admin_exists(self):
        """True if a site admin exists, false otherwise."""
        # see if user exists
        self._cursor.execute("SELECT name FROM 'users' WHERE is_site_admin = ?", (True,))
        exists = self._cursor.fetchone()
        if exists:
            return True
        else:
            return False

    # auth
    def create_user(self, username, password, is_site_admin=False):
        """Create a new user."""
        # see if user exists
        self._cursor.execute("SELECT name FROM 'users' WHERE name = ?", (username,))
        exists = self._cursor.fetchone()
        if exists:
            return False

        # generate password hash
        pepper = passlib.utils.getrandbytes(passlib.utils.rng, 50)
        hash = self.__encrypt_password(password, pepper)
        del password

        # insert into database!
        self._cursor.execute("INSERT INTO 'users' (name, is_site_admin, pepper, pw_hash) VALUES (?, ?, ?, ?)", (username, is_site_admin, pepper, hash))

        return True

    def password_matches(self, username, password):
        """Return whether the given password matches the one in our database."""
        self._cursor.execute("SELECT pw_hash, pepper FROM 'users' WHERE name = ?", (username,))
        row = self._cursor.fetchone()
        # make sure user exists
        if row is None:
            return False
        check_hash, pepper = row

        # compare hashes
        genned_pw = self.__encrypt_password(password, pepper)
        del password
        if genned_pw == check_hash:
            return True
        else:
            return False

    @property
    def __salt(self):
        """Return our salt. If salt doesn't exist, create it!"""
        # get salt
        self._cursor.execute("SELECT salt FROM 'site'")
        salt = self._cursor.fetchone()
        if salt is not None:
            salt = salt[0]

        # if salt doesn't exist, create one
        if salt is None:
            salt = passlib.utils.getrandbytes(passlib.utils.rng, 50)
            self._cursor.execute("INSERT INTO 'site' (salt) VALUES (?)", (salt,))

        return salt

    def __encrypt_password(self, password, pepper):
        """Returns an encrypted password, given the pepper.

        Arguments:
            password is expected to be a UTF-8 string.
            pepper is a blob of bytes.
        """
        pw_bytes = bytes(password, 'utf-8')
        built_pw = bytearray()
        built_pw += pw_bytes
        built_pw += b'|'
        built_pw += pepper
        built_pw += b'|'
        built_pw += self.__salt
        built_pw = bytes(built_pw)
        del pw_bytes
        del password
        hash = pbkdf2_sha512.encrypt(built_pw, salt_size=0)
        del built_pw

        return hash
