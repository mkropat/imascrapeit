class Transaction:
    def __init__(self, src, dest, timestamp, amt, currency, description, fingerprint=None):
        self.fingerprint = fingerprint
        self.src = src
        self.dest = dest
        self.timestamp = timestamp
        self.amt = amt
        self.currency = currency
        self.description = description

    def __repr__(self):
        src = self.src
        if src is None:
            src = 'unknown'

        dest = self.dest
        if dest is None:
            dest = 'unknown'

        return '%s: %s%s from %s to %s' % (self.timestamp.date(), self.currency, self.amt.copy_abs(), src, dest)

