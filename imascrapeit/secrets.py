import base64, contextlib, json, os, os.path, tempfile, time

# pip install cryptography

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecretsStore:
    def __init__(self, store_path, passphrase):
        self._path = store_path
        self._passphrase = passphrase
        self._container = self._read_store(self._path, self._passphrase)

    def __getitem__(self, key):
        return self._container.data.get(key, None)

    def __setitem__(self, key, secret):
        self._container.data[key] = secret

        self._save_store(self._path, self._passphrase, self._container)

    def is_new(self):
        return not os.path.exists(self._path)

    @staticmethod
    def _read_store(path, passphrase):
        if os.path.exists(path):
            with open(path) as f:
                try:
                    return _EncryptionContainer.decrypt(f.read(), passphrase, _SerializableDict.deserialize)
                except InvalidToken:
                    raise InvalidPassphrase()
        else:
            return _EncryptionContainer(_SerializableDict())

    @staticmethod
    def _save_store(path, passphrase, container):
        user_only_mask = 0o77
        with _umask(user_only_mask):
            dirname = os.path.dirname(path)

            os.makedirs(dirname, exist_ok=True)

            with _replace_file(path, dir=dirname) as f:
                buf = container.encrypt(passphrase)
                f.write(buf)

class InvalidPassphrase(Exception): pass

class _EncryptionContainer:
    VERSION = 1

    @classmethod
    def decrypt(klass, buf, passphrase, data_deserializer):
        args = json.loads(buf)

        key = klass._kdf(passphrase, args['salt'], args['rounds'])
        data = data_deserializer(
            Fernet(key).decrypt(args['encrypted'].encode('ascii')))

        return klass(data, rounds=args['rounds'])

    def __init__(self, data, rounds=None):
        self.data = data

        if rounds is None:
            rounds = self._calculate_num_rounds()
        self._rounds = rounds

    def encrypt(self, passphrase):
        salt = self._generate_salt()
        key = self._kdf(passphrase, salt, self._rounds)
        encrypted = Fernet(key).encrypt(self.data.serialize())
        return json.dumps({
            'salt': salt.decode('ascii'),
            'rounds': self._rounds,
            'encrypted': encrypted.decode('ascii'),
            'version': self.VERSION,
        })

    @staticmethod
    def _kdf(passphrase, salt, rounds):
        if isinstance(passphrase, str):
            passphrase = passphrase.encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=base64.urlsafe_b64decode(salt),
            iterations=2**rounds,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase))

    @staticmethod
    def _generate_salt():
        return base64.urlsafe_b64encode(os.urandom(16))

    @classmethod
    def _calculate_num_rounds(klass):
        rounds = 17
        duration = _clock(lambda: klass._kdf(b'test passphrase', b'test salt', rounds))
        while duration < 0.5:
            rounds += 1
            duration = _clock(lambda: klass._kdf(b'test passphrase', b'test salt', rounds))

        return rounds

class _SerializableDict(dict):
    @classmethod
    def deserialize(klass, buf):
        return klass(json.loads(buf.decode('utf-8')))

    def serialize(self):
        return json.dumps(self).encode('utf-8')

@contextlib.contextmanager
def _umask(val):
    orig = None
    try:
        orig = os.umask(val)
        yield
    finally:
        os.umask(orig)

@contextlib.contextmanager
def _replace_file(path, **kws):
    fd, tmp_path = tempfile.mkstemp(**kws)
    safe_to_delete = True

    try:
        with os.fdopen(fd, 'w') as f:
            yield f

        if os.name != 'posix' and os.path.exists(path):
            safe_to_delete = False
            os.remove(path)

        os.rename(tmp_path, path)
    except:
        if safe_to_delete:
            os.remove(tmp_path)

        raise

def _clock(func):
    start = time.perf_counter()
    func()
    end = time.perf_counter()
    return end - start
