import re

from ..amount import parse_usd

class ChaseClient:
    ENTRY_POINT = 'https://www.chase.com/'

    def __init__(self, browser, creds, login_timeout=0):
        self._browser = browser
        self._creds = creds
        self._login_timeout = login_timeout

        self._home_url = None

    def _home(self):
        if self._browser.url != self._home_url:
            self._browser.load(self.ENTRY_POINT)

            self._browser.input_text('#usr_name_home', self._creds.username)
            self._browser.input_text_submit('#usr_password_home', self._creds.password)

            if self._login_timeout:
                self._browser.wait_for('.session_summary', self._login_timeout)

            self._home_url = self._browser.url

    def get_balance(self):
        self._home()

        rows = self._browser.execute("""
        var rows = document.querySelectorAll('table[summary="account information"] > tbody > tr');
        return Array.prototype.map.call(rows, function (r) { return r.innerText.trim() });
        """)

        bal = _first_match(rows, '^Current balance.*([$]\S+)').group(1)

        return -1 * parse_usd(bal)

def _first_match(items, pattern):
    matcher = re.compile(pattern)
    items = (matcher.match(i) for i in items)
    return next((i for i in items if i), None)

new_client = ChaseClient
