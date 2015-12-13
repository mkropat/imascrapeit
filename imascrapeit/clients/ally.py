import csv, datetime, decimal, hashlib, json

from ..amount import parse_usd
from ..transaction import Transaction

class AllyClient:
    ENTRY_POINT = 'https://securebanking.ally.com/'

    def __init__(self, browser, creds, login_timeout=0):
        self._browser = browser
        self._creds = creds
        self._login_timeout = login_timeout

        self._home_url = None

    def _home(self):
        if self._browser.url != self._home_url:
            self._browser.load(self.ENTRY_POINT)

            self._browser.input_text('#username', self._creds.username)
            self._browser.input_text_submit('#password', self._creds.password)
            if self._login_timeout:
                self._browser.wait_for('.welcome .user-name', self._login_timeout)

            self._home_url = self._browser.url

    def get_balance(self):
        self._home()

        return parse_usd(self._browser.get_text('#currentBalance'))

new_client = AllyClient

def import_transactions(path):
    entries = {}

    with open(path) as csv_file:
        reader = csv.DictReader(csv_file, restkey='rest', quoting=csv.QUOTE_NONE, skipinitialspace=True)
        for row in reader:
            if 'rest' in row:
                rest = row.pop('rest')
                last_field = reader.fieldnames[-1]
                row[last_field] = row[last_field] + ',' + ','.join(rest)

            t = create_transaction(row)
            if not t.fingerprint in entries:
                entries[t.fingerprint] = t

    return entries

def create_transaction(row):
    fingerprint = _compute_id(row)

    timestamp = '%s %s' % (row['Date'], row['Time'])
    timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

    src = None
    dest = None

    currency = '$'
    amt = decimal.Decimal(row['Amount'])
    if amt < 0:
        src = 'ally'
    else:
        dest = 'ally'

    return Transaction(src, dest, timestamp, amt, currency, row['Description'], fingerprint)

def _compute_id(dict_):
    serialized = json.dumps(dict_, sort_keys=True)
    return hashlib.sha1(serialized.encode('utf-8')).hexdigest()
