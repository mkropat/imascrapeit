import React from 'react';
import axios from 'axios';

class Login extends React.Component {
  render() {
    return (
      <form onSubmit={evt => this.handleSubmit(evt)}>
        <div className="container">
          <div className="form-group">
            <label htmlFor="passphrase">Passphrase</label>
            <input ref="passphrase" type="password" className="form-control" id="passphrase" />
          </div>
          <button type="submit" className="btn btn-default">Authenticate</button>
        </div>
      </form>
    );
  }

  handleSubmit(evt) {
    evt.preventDefault();

    axios.post('/api/session', {
      passphrase: this.refs.passphrase.value
    })
      .then(() => {
        this.props.history.pushState(null, '/accounts');
      });
  }
}

Login.title = 'Login';

export default Login;
