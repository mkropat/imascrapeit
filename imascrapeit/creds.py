from getpass import getuser
import os.path

from .secrets import SecretsStore, InvalidPassphrase

class CredStore:
    _NAME = 'secrets.db'

    def __init__(self, settings_dir):
        self._path = os.path.join(settings_dir, self._NAME)
        self._store = _NullStore()

    @property
    def user(self):
        return getuser()

    def is_new(self):
        return not os.path.exists(self._path)

    def is_open(self):
        return not isinstance(self._store, _NullStore)

    def open(self, passphrase):
        self._store = _OpenedStore(self._path, passphrase)

    def __contains__(self, account):
        return account in self._store

    def __getitem__(self, account):
        return self._store[account]

    def __setitem__(self, account, creds):
        self._store[account] = creds

    def __delitem__(self, account):
        del self._store[account]

class _OpenedStore:
    def __init__(self, path, passphrase):
        self._store = SecretsStore(path, passphrase)
        if not os.path.exists(path):
            self._store['meta:version'] = 1

    def __contains__(self, account):
        return self._store['account:' + account] is not None

    def __getitem__(self, account):
        if account in self:
            return self._store['account:' + account]

    def __setitem__(self, account, password):
        self._store['account:' + account] = password

    def __delitem__(self, account):
        del self._store['account:' + account]

class _NullStore:
    def __contains__(self, account):
        return False

    def __getitem__(self, account):
        pass

    def __setitem__(self, account, creds):
        raise Exception('not implemented')

    def __delitem__(self, account):
        raise Exception('not implemented')
