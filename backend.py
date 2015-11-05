import contextlib, functools, os, os.path, sqlite3, webbrowser

from flask import Flask, jsonify, request, Response, session
from marshmallow import fields, Schema, ValidationError
from werkzeug.exceptions import BadRequest

from imascrapeit import dirs
from imascrapeit.account import Accounts
from imascrapeit.balance import BalanceHistory
from imascrapeit.creds import CredStore
from imascrapeit.secrets import SecretsStore, InvalidPassphrase
from imascrapeit.store import DbMigrator

app = Flask(__name__)
app.secret_key = os.urandom(24)

cred_store = CredStore(dirs.settings())

port = 10420

def run(debug=True, open_browser=False):
    if open_browser:
        webbrowser.open('http://localhost:{port}/'.format(port=port))

    app.run(
        debug=debug,
        port=port,
        threaded=False) # single-user, low-concurrency app for now

def requires_auth(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            return jsonify(message='Must be logged in'), 400
        else:
            return f(*args, **kwargs)

    return wrapper

def _schema_jsonify(Schema, *args, **kwargs):
    obj = dict(*args, **kwargs)
    serialized = Schema().dump(obj).data
    return jsonify(serialized)

@app.errorhandler(ValidationError)
def validation_error_handler(err):
    return jsonify(
        type='validation-error',
        fields=err.messages), 400

def _schema_parse(Schema, data):
    return Schema(strict=True).load(data).data

class SessionSchema(Schema):
    is_authenticated = fields.Boolean()
    is_setup = fields.Boolean(dump_only=True)
    username = fields.Str(dump_only=True)
    passphrase = fields.Str(load_only=True)

    parse = classmethod(_schema_parse)
    jsonify = classmethod(_schema_jsonify)

class RequestSchema(Schema):
    class Meta:
        fields = ("id",)

requests = {}
@app.routes'/api/requests')
def get_requests():
    pass

@app.route('/api/session', methods=['GET', 'POST'])
def do_session():
    if request.method == 'POST':
        body = SessionSchema.parse(request.get_json())
        if 'is_authenticated' in body and not body['is_authenticated']:
            session['is_authenticated'] = False
        elif 'passphrase' in body:
            try:
                cred_store.open(body['passphrase'])
                session['is_authenticated'] = True
            except InvalidPassphrase:
                return jsonify(message='Invalid passphrase'), 400

        return '', 204

    return SessionSchema.jsonify(
        is_authenticated=is_authenticated(),
        is_setup=cred_store.is_new(),
        username=cred_store.user)

@contextlib.contextmanager
def open_table(func):
    db_dir = os.path.join(dirs.settings(), 'history.db')
    with contextlib.closing(sqlite3.connect(db_dir)) as db:
        migrator = DbMigrator(db)
        yield func(db, migrator)

@app.route('/api/accounts', methods=['GET', 'POST'])
@requires_auth
def get_accounts():
    if request.method == 'GET':
        with open_table(Accounts) as account_store:
            with open_table(BalanceHistory) as history:
                names = [a.name for a in account_store.list()]
                balances = dict((n, history.get_current(n)) for n in names)
                accounts = [
                    account_entry(n, balances[n], cred_store[n]) for n in names
                ]
                total = sum(b.amount for b in balances.values())

                return jsonify(
                    accounts=accounts,
                    summary={ 'balance': str(total) })

    elif request.method == 'POST':
        body = request.get_json() or {}

class AccountSchema(Schema):
    name = fields.Str(required=True)

def account_entry(name, balance, creds=None):
    entry = {
        'name': name,
        'balance': {
            'current': str(entry.amount),
            'last_updated': entry.timestamp.isoformat()
        }
    }

    if creds is not None:
        entry['creds'] = {
            'username': creds.username
        }

    return entry

@app.route('/api/accounts/<account>/creds', methods=['PUT'])
@requires_auth
def set_creds(account):
    raise NotImplementedError()

def is_authenticated():
    if 'is_authenticated' in session:
        return bool(session['is_authenticated'])
    else:
        return False
