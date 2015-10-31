import getpass, os.path

from .secrets import SecretsStore, InvalidPassphrase

class CredShell:
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

class Cred:
    def __init__(self, username, password):
        self.username = username
        self.password = password
