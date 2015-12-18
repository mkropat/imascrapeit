class Notifier {
  constructor() {
    this._listeners = [];
    this._id = 0;
  }

  listen(callback) {
    this._listeners[this._id] = callback;
    let id = this._id++;

    return () => {
      delete this._listeners[id];
    };
  }

  notify() {
    let args = Array.prototype.slice.call(arguments, 0);
    this._listeners.forEach(cb => {
      cb.apply(null, args);
    });
  }
}

export default Notifier;
