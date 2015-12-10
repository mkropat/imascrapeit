window.jQuery = window.$ = require('jquery/dist/jquery.min');
require('bootstrap-webpack');

import React from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { Router, Route, Link } from 'react-router'

import App from './Main';


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

    axios.post('/api/session', {
      passphrase: this.refs.passphrase.value
    })
      .then(() => {
        this.props.history.pushState(null, '/accounts');
      });
  }
}

class Accounts extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      accounts: [],
      summary: {},
      updateStatus: 'ready'
    };
  }

  componentWillMount() {
    this.getAccounts();
  }

  getAccounts() {
    axios.get('/api/accounts')
      .then(r => {
        this.setState({
          accounts: r.data.accounts || [],
          summary: r.data.summary || {}
        });
      });
  }

  updateAccounts() {
    axios.post('/api/accounts', {
      action: 'update'
    })
      .then(r => {
        this.setState({
          updateStatus: r.data.status
        });

        this.pollWhilePending(r.data._links.self.href);
      });
  }

  pollWhilePending(url) {
    setTimeout(() => this.poll(url), 1000);
  }

  poll(url) {
    axios.get(url)
      .then(r => {
        this.setState({
          updateStatus: r.data.status
        });

        if (this.state.updateStatus === 'pending') {
          this.pollWhilePending(url);
        }
        else {
          this.getAccounts();
        }
      });
  }

  render() {
    const rows = this.state.accounts.map(a =>
      <tr key={a.id}>
        <td>{a.id}</td>
        <td>{a.balance.current}</td>
      </tr>);

    return (
      <div className="container">
        <h2>Accounts</h2>
        <table className="table">
          <thead>
            <tr><th>Name</th><th>Balance</th></tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
          <tfoot>
            <tr><th>Total</th><td>{this.state.summary.balance}</td></tr>
          </tfoot>
        </table>
        <button className="btn btn-primary"
          disabled={this.state.updateStatus === 'pending' ? 'disabled' : ''}
          onClick={() => this.updateAccounts()}>
          {this.state.updateStatus === 'pending' ? 'Updating...' : 'Update Accounts'}
        </button>
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
