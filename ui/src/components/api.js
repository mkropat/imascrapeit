class ApiClient {
  constructor (base) {
    this._base = base;
  }

  get (url) {
    return window.fetch(this._base + url, { credentials: 'include' })
      .then(r => r.json());
  }

  post (url, data) {
    let headers = new Headers();
    headers.append('Accept', 'application/json');
    headers.append('Content-Type', 'application/json');

    let options = {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(data),
      credentials: 'include'
    };
    return window.fetch(this._base + url, options)
      .then(r => r.json());
  }
}

let api = new ApiClient('/api');

export default api;
