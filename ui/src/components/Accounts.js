import React from 'react';
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
        <td>{moment(a.balance.last_updated).fromNow()}</td>
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

Accounts.title = 'Accounts';

export default Accounts;
