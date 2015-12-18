from collections import namedtuple
import functools
import os
import os.path
import traceback

from contextlib import closing

from flask import g, Flask, jsonify, redirect, request, Response, session
from marshmallow import fields, Schema, ValidationError
from werkzeug.exceptions import BadRequest

from imascrapeit import dirs, driver
from imascrapeit.account import Accounts
from imascrapeit.balance import BalanceEntry, BalanceHistory
from imascrapeit.chrome import open_chrome
from imascrapeit.creds import CredStore
from imascrapeit.duration import minutes
from imascrapeit.requests import AsyncRequestTracker
from imascrapeit.secrets import SecretsStore, InvalidPassphrase
from imascrapeit.store import DbContext
from imascrapeit.threads import BackgroundRunner

app = Flask(__name__)
#app.secret_key = os.urandom(24)
app.secret_key = b'\x80<\xd9\x19\xec-\x9d\x81F2\xeb\xfcM\x16\rXG\xd0(l\x98\x12\xf2\xf9'

background = BackgroundRunner()

cred_store = CredStore(dirs.settings())

port = 10420

_is_debug=False

def run(debug=True):
    global _is_debug
    _is_debug = debug

    with closing(_open_db()) as db:
        db.init_tables()

    app.run(
        debug=debug,
        port=port,
        threaded=True)

    background.join()

def _open_db():
    path = os.path.join(dirs.settings(), 'history.db')
    return DbContext(path, {
        'accounts': Accounts,
        'balance_history': BalanceHistory,
    })

def _db():
    db = getattr(g, '_db', None)
    if db is None:
        db = _open_db()

    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_db', None)
    if db is not None:
        db.close()

def requires_auth(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            return jsonify(message='Must be logged in'), 403
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

@app.route('/api')
def entry_point():
    return jsonify(name='This is an imascrapeit API')

requests = AsyncRequestTracker()

@app.route('/api/requests')
@requires_auth
def list_requests():
    return jsonify(requests=requests.list())

def _dump_tuple(t):
    return dict((k, v) for k, v in vars(t).items() if v is not None)

@app.route('/api/requests/<request_id>')
@requires_auth
def get_request(request_id):
    try:
        r = requests[request_id]

        body = _dump_tuple(r)
        body['_links'] = {
            'self': { 'href': '/api/requests/{}'.format(r.id) }
        }
        if r.created_url is not None:
            body['_links']['created'] = { 'href': r.created_url }
            del body['created_url']

        resp = jsonify(**body)

        if r.status == 'pending':
            resp.status_code = 202
        elif r.created_url is not None:
            resp.status_code = 201
            resp.headers['Location'] = r.created_url

        return resp
    except KeyError:
        return jsonify(message='No such request'), 404

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
                if _is_debug:
                    session['passphrase'] = body['passphrase']
            except InvalidPassphrase:
                return jsonify(message='Invalid passphrase'), 400

        return '', 204

    return SessionSchema.jsonify(
        is_authenticated=is_authenticated(),
        is_setup=cred_store.is_new(),
        username=cred_store.user)

@app.route('/api/accounts', methods=['GET', 'POST'])
@requires_auth
def get_accounts():
    if request.method == 'GET':
        accounts =  _db().accounts.list()
        balances = dict((a.id, _db().balance_history.get_current(a.id)) for a in accounts)
        accounts = [
            account_entry(a, balances[a.id]) for a in accounts
        ]
        total = sum(b.amount for b in balances.values())

        return jsonify(
            accounts=accounts,
            summary={ 'balance': str(total) })

    elif request.method == 'POST':
        body = BulkAccountSchema.parse(request.get_json())

        if body['action'] == 'create':
            body = NewAccountSchema.parse(request.get_json())

            body_sanitized = body.copy()
            body_sanitized['password'] = '*'*len(body_sanitized['password'])

            r = requests.new(body_sanitized)

            driver.get_factory(body['driver'])

            background.run(_create_account,
                body['name'],
                body['driver'],
                body['username'],
                body['password'],
                r)

            return redirect('/api/requests/{}'.format(r.id), code=303)

        elif body['action'] == 'update':
            r = requests.new()
            background.run(_update_accounts, r)
            return redirect('/api/requests/{}'.format(r.id), code=303)

        else:
            return jsonify(message='Unsupported action'), 400


@app.route('/api/accounts/<id_>', methods=['GET', 'DELETE'])
@requires_auth
def get_account(id_):
    if request.method == 'GET':
        try:
            a = _db().accounts[id_]
            balance = _db().balance_history.get_current(a.id)

            resp = account_entry(a, balance)
            resp['_links'] = {
                'self': { 'href': '/api/accounts/{}'.format(id_) },
            }

            return jsonify(**resp)
        except KeyError:
            return jsonify(message='No such acccount'), 404

    elif request.method == 'DELETE':
        db = _db()
        with db:
            del db.accounts[id_]
            db.balance_history.delete_history(id_)
            del cred_store[id_]
        return '', 204

@app.route('/api/drivers')
@requires_auth
def get_drivers():
    return jsonify(drivers=driver.list())

def _create_account(name, driver_name, username, password, request_resolver):
    try:
        with closing(_open_db()) as db:
            with open_chrome(dirs.chrome_profile('ImaScrapeIt Profile')) as browser:
                client_factory = driver.get_factory(driver_name)
                client = client_factory(browser, Cred(username, password), login_timeout=minutes(5))
                bal = client.get_balance()

                account = None
                with db:
                    account = db.accounts.create(name, driver_name, username)
                    db.balance_history.add(BalanceEntry(account.id, bal))
                    cred_store[account.id] = password

                request_resolver.resolve(created_url='/api/accounts/{}'.format(account.id))
    except Exception:
        request_resolver.reject(traceback.format_exc())

Cred = namedtuple('Cred', ['username', 'password'])

def _update_accounts(request_resolver):
    try:
        with closing(_open_db()) as db:
            with open_chrome(dirs.chrome_profile('ImaScrapeIt Profile')) as browser:
                with db:
                    for a in db.accounts.list():
                        client_factory = driver.get_factory(a.driver)
                        client = client_factory(
                            browser,
                            Cred(a.username, cred_store[a.id]),
                            login_timeout=minutes(5))

                        bal = client.get_balance()

                        db.balance_history.add(BalanceEntry(a.id, bal))

        request_resolver.resolve()
    except Exception:
        request_resolver.reject(traceback.format_exc())

class BulkAccountSchema(Schema):
    action = fields.Str(required=True)

    parse = classmethod(_schema_parse)

class NewAccountSchema(Schema):
    name = fields.Str(required=True)
    driver = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)

    parse = classmethod(_schema_parse)

def account_entry(account, balance):
    return {
        'id': account.id,
        'name': account.name,
        'driver': account.driver,
        'balance': {
            'current': str(balance.amount),
            'last_updated': balance.timestamp.isoformat() + 'Z',
        },
        'creds': {
            'username': account.username
        }
    }

@app.route('/api/accounts/<account>/creds', methods=['PUT'])
@requires_auth
def set_creds(account):
    raise NotImplementedError()

def is_authenticated():
    if not cred_store.is_open() and 'passphrase' in session:
        cred_store.open(session['passphrase'])
    return is_browser_auth() and cred_store.is_open()

def is_browser_auth():
    if 'is_authenticated' in session:
        return bool(session['is_authenticated'])
    else:
        return False
