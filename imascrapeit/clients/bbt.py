#!/usr/bin/env python3

import contextlib, csv, datetime, decimal, hashlib, json, re

from dateutil import relativedelta

from ..amount import parse_usd
from ..transaction import Transaction

class BbtClient:
    def __init__(self, browser, creds, login_timeout=0):
        self._browser = browser
        self._creds = creds
        self._login_timeout = login_timeout

        self._home_url = None

    def _home(self):
        if self._browser.url != self._home_url:
            self._browser.load('https://www.bbt.com/')

            self._browser.input_text_submit('#usernamefield', self._creds.username)
            self._browser.input_text_submit('#user-password', self._creds.password)
            if self._login_timeout:
                self._browser.wait_for('.welcome-text .person-name', self._login_timeout)

            self._home_url = self._browser.url

    def get_balance(self):
        self._home()

        return parse_usd(self._browser.get_text('#defaultCash .acct-overview-right-column'))

    @contextlib.contextmanager
    def open_transactions(self):
        self._home()

        browser.click('#defaultCash a')
        browser.click('.exportlink a')

        start_date = datetime.date.today() - relativedelta.relativedelta(years=1)
        browser.override_text('#exportStartStr', start_date.strftime('%m/%d/%Y'))

        browser.watch_download_dir()

        browser.click('#export-history .submit-button')

        with browser.open_download() as f:
            browser.click('#home a')

            yield f

new_client = BbtClient

def import_transactions(path):
    entries = {}

    with open(path) as csv_file:
        for row in csv.DictReader(csv_file):
            t = _create_transaction(row)
            if not t.fingerprint in entries:
                entries[t.fingerprint] = t

    return entries

def _create_transaction(row):
    fingerprint = _compute_id(row)
    timestamp = datetime.datetime.strptime(row['Date'], '%m/%d/%Y')
    src = None
    dest = None

    debit_match = re.match('^\((.)([0-9.]*)\)$', row['Amount'])
    credit_match = re.match('^(.)([0-9.]*)$', row['Amount'])
    if debit_match:
        currency = debit_match.group(1)
        amt = -1 * decimal.Decimal(debit_match.group(2))
        src = 'bbt'
    elif credit_match:
        currency = credit_match.group(1)
        amt = decimal.Decimal(credit_match.group(2))
        dest = 'bbt'

    return Transaction(src, dest, timestamp, amt, currency, row['Description'], fingerprint)

def _compute_id(dict_):
    serialized = json.dumps(dict_, sort_keys=True)
    return hashlib.sha1(serialized.encode('utf-8')).hexdigest()
