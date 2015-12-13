import axios from 'axios';

class AccountsResource {
  constructor() {
    this._listCache = null;
    this._getCache = {};
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

  update() {
    return axios.post('/api/accounts', {
      action: 'update'
    });
  }
}

export default AccountsResource;
