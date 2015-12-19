import React from 'react';
import { Link } from 'react-router'
import axios from 'axios';
import moment from 'moment/moment';

class Accounts extends React.Component {
  constructor(props) {
    super(props);

    this._listenCanceler = null;
    this.state = {
      _links: {},
      accounts: [],
      summary: {},
      isUpdating: false,
    };
  }

  componentWillMount() {
    this.getList();
  }

  isViewingThisComponent(props) {
    let leafRoute = props.routes[props.routes.length - 1];
    return leafRoute && leafRoute.component === Accounts;
  }

  componentWillReceiveProps(newProps) {
    if (this.isViewingThisComponent(newProps)) {
      this.getList();
    }
  }

  getList() {
    this.props.route.accountsResource.list().then(r => {
      this.setState({
        _links: r.data._links || {},
        accounts: r.data._embedded.accounts || [],
        summary: r.data.summary || {}
      });
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
    return this.state._links.update && !this.state.isUpdating;
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

    let link = this.state._links.update;
    this.props.route.accountsResource.actionTillComplete(link.method, link.href, {
      action: 'update'
    })
      .then(stopUpdating, stopUpdating);
  }

  componentWillUnmount() {
    if (this._listenCanceler) {
      this._listenCanceler();
    }
  }
}

Accounts.title = 'Accounts';

export default Accounts;
