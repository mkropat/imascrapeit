import collections
import getpass
import os.path

from .secrets import SecretsStore, InvalidPassphrase

class CredStore:
    _NAME = 'secrets.db'

    def __init__(self, settings_dir):
        self._path = os.path.join(settings_dir, self._NAME)
        self._store = _NullStore()

    @property
    def user(self):
        return getpass.getuser()

    def is_new(self):
        return os.path.exists(self._path)

    def open(self, passphrase):
        self._store = _OpenedStore(self._path, passphrase)

    def __contains__(self, account):
        return account in self._store

    def __getitem__(self, account):
        return self._store[account]

    def __setitem__(self, account, creds):
        self._store[account] = creds

class _OpenedStore:
    def __init__(self, path, passphrase):
        self._store = SecretsStore(path, passphrase)
        if not os.path.exists(path):
            self._store['meta:version'] = 1

    def __contains__(self, account):
        return self._store[account + ':username'] is not None

    def __getitem__(self, account):
        if account in self:
            return Cred(
                self._store[account + ':username'],
                self._store[account + ':password'])

    def __setitem__(self, account, creds):
        self._store[account + ':username'] = creds.username
        self._store[account + ':password'] = creds.password

class _NullStore:
    def __contains__(self, account):
        return False

    def __getitem__(self, account):
        pass

    def __setitem__(self, account, creds):
        raise Exception('not implemented')

class CliCredShell:
    def __init__(self, settings_dir):
        self._path = os.path.join(settings_dir, 'secrets.db')
        self._store = None

    def __getitem__(self, account):
        self._open()
        self._populate(account)

        return Cred(
            self._store[account + ':username'],
            self._store[account + ':password'])

    def _open(self):
        while not self._store:
            try:
                passphrase = getpass.getpass('Secrets DB Passphrase: ')
                self._store = SecretsStore(self._path, passphrase)
            except InvalidPassphrase:
                print('Invalid passphrase.  Please try again.')

    def _populate(self, account):
        if self._store[account + ':username'] is None:
            print('Enter credentials for your "%s" account' % account)
            self._store[account + ':username'] = input('Username: ')
            self._store[account + ':password'] = self._read_password('Password')

    @staticmethod
    def _read_password(prompt):
        def do_prompt():
            return (
                getpass.getpass(prompt + ': '),
                getpass.getpass('confirm: '))

        pw1, pw2 = do_prompt()
        while pw1 != pw2:
            print('Passwords do not match.  Please try again.')
            pw1, pw2 = do_prompt()

        return pw1

Cred = collections.namedtuple('Cred', ['username', 'password'])
