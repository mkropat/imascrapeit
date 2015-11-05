import babel.numbers, decimal, locale, re

class Amount:
    def __init__(self, currency, amount):
        self.currency = currency
        self.amount = decimal.Decimal(amount)

    @classmethod
    def null(klass):
        return klass(None, 0)

    @classmethod
    def parse(klass, currency, amount, locale=None):
        if locale is None:
            locale = klass._user_locale()

        return klass(currency, klass._parse_amount(amount, locale))

    @staticmethod
    def _parse_amount(amount, locale):
        if isinstance(amount, decimal.Decimal):
            return amount
        else:
            return babel.numbers.parse_decimal(amount, locale)

    def __add__(self, other):
        if other == 0 or not other.amount:
            return self
        elif self.currency != other.currency:
            raise ValueError('Currencies may not differ: %s vs %s' %
                    (self.currency, other.currency))
        return Amount(self.currency, self.amount + other.amount)

    __radd__ = __add__

    def __mul__(self, other):
        return Amount(self.currency, self.amount * other)

    __rmul__ = __mul__

    def __repr__(self):
        if not self.currency and not self.amount:
            return '0'
        else:
            return babel.numbers.format_currency(
                self.amount,
                self.currency,
                locale=self._user_locale())

    @staticmethod
    def _user_locale():
        return locale.getdefaultlocale()[0]

def parse_usd(text):
    match = re.match('^[$]?([0-9,.]+)$', text)
    if match:
        return Amount.parse('USD', match.group(1), locale='en_US')
