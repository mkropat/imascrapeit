from collections import namedtuple
from datetime import datetime
from uuid import uuid4

AsyncRequest = namedtuple('AsyncRequest', [
    'completed_at',
    'created_url',
    'error',
    'id',
    'request',
    'started_at',
    'status',
])

class AsyncRequestTracker:
    def __init__(self):
        self._requests = {}

    def list(self):
        return list(self._requests.keys())

    def __getitem__(self, id_):
        return self._requests[id_]

    def new(self, request=None):
        r = AsyncRequest(
            completed_at=None,
            created_url=None,
            error=None,
            id=str(uuid4()),
            request=request,
            status='pending',
            started_at=datetime.utcnow())

        self._requests[r.id] = r

        return _AsyncRequestResolver(
            id=r.id,
            tracker=self)

    def _update(self, id_, **kwargs):
        if self._requests[id_].status != 'pending':
            raise Exception('Request has already been resolved')

        self._requests[id_] = self._requests[id_]._replace(**kwargs)

class _AsyncRequestResolver(namedtuple('AsyncRequestResolver', ['id', 'tracker'])):
    def resolve(self):
        self.tracker._update(self.id,
            completed_at=datetime.utcnow(),
            status='success')

    def reject(self, error=None):
        print(error)
        self.tracker._update(self.id,
            completed_at=datetime.utcnow(),
            error=error,
            status='fail')
