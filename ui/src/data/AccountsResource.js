import axios from 'axios';

class AccountsResource {
  constructor() {
    this._listCache = null;
    this._getCache = {};
    this._listeners = [];
    this._listenerId = 1;
  }

  listen(cb) {
    this._listeners[this._listenerId] = cb;
    let id = this._listenerId++;
    return () => {
      delete this._listeners[id];
    }
  }

  _notify(data) {
    this._listeners.forEach(cb => {
      cb(data);
    });
  }

  list() {
    return this._listCache
      ? Promise.resolve(this._listCache)
      : this.listFresh();
  }

  listFresh() {
    return axios.get('/api/accounts')
      .then(r => {
        this._listCache = r.data;

        this._getCache = {};
        this._listCache.accounts.forEach(a => {
          this._getCache[a.id] = a;
        });

        setTimeout(() => {
          this._notify(this._listCache);
        });

        return this._listCache;
      });
  }

  get(id) {
    return this._getCache.hasOwnProperty(id)
      ? Promise.resolve(this._getCache[id])
      : this.getFresh(id);
  }

  getFresh(id) {
    return axios.get('/api/accounts/' + id)
      .then(r => {
        this._getCache[id] = r.data;

        return this._getCache[id];
      });
  }

  add(name, driver, username, password) {
    var p = axios.post('/api/accounts', {
      action: 'create',
      name: name,
      driver: driver,
      username: username,
      password: password
    })
      .then(r => pollWhilePending(r.data._links.self.href));
    p.then(() => this.listFresh());
    return p;
  }

  update() {
    var p = axios.post('/api/accounts', {
      action: 'update'
    })
      .then(r => pollWhilePending(r.data._links.self.href));
    p.then(() => this.listFresh());
    return p;
  }

  delete(id) {
    id = '' + id;
    if (!id) {
      throw new Error('Expected an id');
    }
    var p = axios.delete('/api/accounts/' + id);
    p.then(() => this.listFresh());
    return p;
  }
}

function pollWhilePending(url) {
  return axios.get(url)
    .then(r => {
      return r.data.status === 'pending'
        ? delay(1000).then(() => pollWhilePending(url))
        : r;
    });
}

function delay(ms) {
  return new Promise(r => setTimeout(r, ms));
}

export default AccountsResource;
