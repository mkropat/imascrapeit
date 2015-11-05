window.jQuery = window.$ = require('jquery/dist/jquery.min');
require('bootstrap-webpack');

import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Route, Link } from 'react-router'
import App from './Main';
import api from './api';

class Initialize extends React.Component {
  render() {
    return <p>Initialize screen</p>
  }
}
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

    api.post('/session', {
      passphrase: this.refs.passphrase.value
    })
      .then(() => {
        this.props.history.pushState(null, '/accounts');
      });

    console.log('passphrase', this.refs.passphrase.value);
  }
}

class Accounts extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      accounts: []
    };
  }

  componentWillMount() {
    api.get('/accounts')
      .then(r => {
        let accounts = r.accounts || [];
        this.setState({
          accounts: accounts
        });
      });
  }

  render() {
    let rows = this.state.accounts.map(a => <li key={a}>{a}</li>);
    return (
      <div>
        <h2>Accounts screen</h2>
        <ul>{rows}</ul>
      </div>
    );
  }
}

// Render the main component into the dom
//ReactDOM.render(<App />, document.getElementById('app'));
ReactDOM.render((
  <Router>
    <Route path="/" component={App}>
      <Route path="init" component={Initialize} />
      <Route path="login" component={Login} />
      <Route path="accounts" component={Accounts} />
    </Route>
  </Router>
), document.getElementById('app'))
