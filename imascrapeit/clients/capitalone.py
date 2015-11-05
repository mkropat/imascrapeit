from ..amount import parse_usd

class CapitalOneCreditCardClient:
    def __init__(self, browser, creds, login_timeout=0):
        self._browser = browser
        self._creds = creds
        self._login_timeout = login_timeout

        self._home_url = None

    def _home(self):
        if self._browser.url != self._home_url:
            self._browser.load('https://servicing.capitalone.com/c1/Login.aspx')

            with self._browser.enter_iframe('#loginframe'):
                self._browser.input_text('#uname', self._creds.username)
                self._browser.input_text_submit('#cofisso_ti_passw', self._creds.password)

            if self._login_timeout:
                self._browser.wait_for('#section_header_customer_name', self._login_timeout)

            self._home_url = self._browser.url

    def get_balance(self):
        self._home()

        return -1 * parse_usd(self._browser.get_text('#acct0_current_balance_amount'))

new_client = CapitalOneCreditCardClient
