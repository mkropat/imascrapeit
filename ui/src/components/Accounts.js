import React from 'react';
import { Link } from 'react-router'
import axios from 'axios';
import moment from 'moment/moment';

class Accounts extends React.Component {
  constructor(props) {
    super(props);

    this._listenerId = null;
    this.state = {
      accounts: [],
      summary: {},
      isUpdating: false,
    };
  }

  componentWillMount() {
    this._listenerId = this.props.route.accountsResource.listen(r => {
      this.setState({
        accounts: r.accounts || [],
        summary: r.summary || {}
      });
    });

    this.props.route.accountsResource.listFresh()
  }

  render() {
    if (this.props.children) {
      return <div>{this.props.children}</div>
    }

    const rows = this.state.accounts.map(a =>
      <tr key={a.id}>
        <td>
          <Link to={`/accounts/${a.id}`}>
            {a.name}
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
            {this.state.isUpdating ? 'Updating...' : 'Update Accounts'}
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
    return this.state.accounts.length && !this.state.isUpdating;
  }

  formatTimestamp(ts) {
    return moment(ts).fromNow();
  }

  updateAccounts() {
    this.setState({
      isUpdating: true,
    });

    let stopUpdating = () => {
      this.setState({
        isUpdating: false
      });
    };

    this.props.route.accountsResource.update()
      .then(stopUpdating, stopUpdating);
  }

  componentWillUnmount() {
    this.props.route.accountsResource.stopListening(this._listenerId);
  }
}

Accounts.title = 'Accounts';

export default Accounts;
