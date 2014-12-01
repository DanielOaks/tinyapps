#!/usr/bin/env python3
# TinyApps - Configuration Store
# written by Daniel Oaks <daniel@danieloaks.net>
# licensed under the BSD 2-clause license
import os
import json

# config
config_defaults = {
    'allow_external_ips': False,
    'allow_registration': False,
    'allow_registration_from_remote': False,
}


class TinyConfig:
    """Stores the site config for a TinyApps instance."""
    def __init__(self, path):
        self._path = path
        self._config = {}

        self.load()

    def load(self):
        """Load from our config file."""
        if os.sep in self._path:
            folder = self._path.rsplit(os.sep, 1)[0]
            if not os.path.exists(folder):
                os.makedirs(folder)
        try:
            with open(self._path, 'r') as config_file:
                self._config = json.loads(config_file.read())
        except:
            pass

    def save(self):
        """Save to our config file."""
        if os.sep in self._path:
            folder = self._path.rsplit(os.sep, 1)[0]
            if not os.path.exists(folder):
                os.makedirs(folder)
        with open(self._path, 'w') as config_file:
            config_file.write(json.dumps(self._config, indent=4, sort_keys=True))
            config_file.write('\n')

    @property
    def finished(self):
        for name in config_defaults:
            if name not in self._config:
                return False
        return True

    # attributes
    def __getattr__(self, name):
        if name in self._config:
            return self._config[name]
        elif name in config_defaults:
            return config_defaults[name]
        else:
            try:
                return self.__dict__[name]
            except:
                raise AttributeError('Attribute {} does not exist'.format(name))

    def __setattr__(self, name, value):
        if name in config_defaults:
            self._config[name] = value
        else:
            super().__setattr__(name, value)
