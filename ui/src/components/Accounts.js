import React from 'react';
import { Link } from 'react-router'
import axios from 'axios';
import moment from 'moment/moment';

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
    this.props.route.accountsResource.list()
      .then(r => {
        this.setState({
          accounts: r.accounts || [],
          summary: r.summary || {}
        });
      });
  }

  updateAccounts() {
    this.props.route.accountsResource.update()
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
    if (this.props.children) {
      return <div>{this.props.children}</div>
    }

    const rows = this.state.accounts.map(a =>
      <tr key={a.id}>
        <td>
          <Link to={`/accounts/${a.id}`}>
            {a.id}
          </Link>
        </td>
        <td>{a.balance.current}</td>
        <td>{this.formatTimestamp(a.balance.last_updated)}</td>
      </tr>);

    return (
      <div className="container">
        <h2>Accounts</h2>
        <table className="table">
          <thead>
            <tr><th>Name</th><th>Balance</th><th>Last Updated</th></tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
          <tfoot>
            <tr><th>Total</th><td>{this.state.summary.balance}</td><td>&nbsp;</td></tr>
          </tfoot>
        </table>
        <div className="btn-toolbar">
        <button className="btn btn-primary"
          disabled={this.canUpdateAccounts() ? '' : 'disabled'}
          onClick={() => this.updateAccounts()}>
          {this.state.updateStatus === 'pending' ? 'Updating...' : 'Update Accounts'}
        </button>
        <Link
          to="/accounts/new"
          className="btn btn-default">
          Add Account
        </Link>
        </div>
      </div>
    );
  }

  canUpdateAccounts() {
    return this.state.updateStatus !== 'pending' && this.state.accounts.length;
  }

  formatTimestamp(ts) {
    return moment(ts).fromNow();
  }
}

Accounts.title = 'Accounts';

export default Accounts;
