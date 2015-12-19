import axios from 'axios';

class AccountsResource {
  constructor() {
  }

  list() {
    return axios.get('/api/accounts');
  }

  get(id) {
    return axios.get('/api/accounts/' + id);
  }

  action(method, href, data) {
    method = method || 'post';

    return axios({
      method: method,
      url: href,
      data: data
    });
  }

  actionTillComplete(method, href, data) {
    return this.action(method, href, data)
      .then(r => pollWhilePending(r.data._links.self.href));
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
