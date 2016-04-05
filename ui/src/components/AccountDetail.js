import React from 'react';
import moment from 'moment/moment';
import { Link } from 'react-router'

class AccountDetail extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      account: {},
      isDeleting: false,
      deleteLink: null,
      updateLink: null,
    };
  }

  componentWillMount() {
    this.loadAccount(this.props.params.id);
  }

  componentWillReceiveProps(newProps) {
    if (this.props.params.id !== newProps.params.id) {
      this.loadAccount(newProps.params.id);
    }
  }

  loadAccount(id) {
    this.props.route.accountsResource.get(id)
      .then(r => {
        this.setState({
          account: r.data,
          deleteLink: r.data._links.delete,
          updateLink: r.data._links.update_password,
        });

        this.props.route.breadcrumbNotifier.notify(AccountDetail, r.data.name);
      });
  }

  updateField(evt) {
    let newState = {};
    newState[evt.target.id] = evt.target.value;
    this.setState(newState);
  }

  render() {
    let account = this.state.account;
    let balance = account.balance || {};

    return (
      <div className="container">
        <h2>Detail</h2>
        <p>Name: {account.name}</p>
        <p>Balance: {balance.current}</p>
        <p>Last Updated: {this.formatTimestamp(balance.last_updated)}</p>

        <div className="form-group">
          <label htmlFor="password">New Password</label>
          <input type="password" className="form-control" onChange={this.updateField.bind(this)} value={this.state.password} id="password" />
        </div>

        <div className="form-group">
          <div className="btn-toolbar">
            <button type="button"
              className="btn btn-primary"
              onClick={() => this.updateAccount()}>
              Update Account
            </button>
            <button type="button"
              className="btn btn-default"
              disabled={this.canDelete() ? '' : 'disabled'}
              onClick={() => this.confirmDelete()}>
              {this.state.isDeleting ? 'Deleting...' : 'Delete Account'}
            </button>
          </div>
        </div>

        <div className="modal fade"
          tabIndex="-1"
          role="dialog"
          ref={e => this._modal = e}>

          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <button type="button" className="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 className="modal-title">Confirm Delete</h4>
              </div>
              <div className="modal-body">
                <p>Are you sure you want to delete the "{account.name}" account?</p>
              </div>
              <div className="modal-footer">
                <button type="button"
                  className="btn btn-primary"
                  data-dismiss="modal"
                  onClick={() => this.deleteAccount()}>
                  Delete
                </button>
                <button type="button" className="btn btn-link" data-dismiss="modal">Cancel</button>
              </div>
            </div>
          </div>

        </div>
      </div>
    );
  }

  updateAccount() {
    let link = this.state.updateLink;
    this.props.route.accountsResource.action(link.method, link.href, {
      password: this.state.password
    })
      .then(() => this.setState({ password: '' }));
  }

  canDelete() {
    return this.state.deleteLink && !this.state.isDeleting;
  }

  confirmDelete() {
    if (this._modal) {
      jQuery(this._modal).modal();
    }
  }

  deleteAccount() {
    this.setState({
      isDeleting: true
    });

    let link = this.state.deleteLink;
    this.props.route.accountsResource.action(link.method, link.href)
      .then(r => {
        this.props.history.push('/accounts');
      });
  }

  formatTimestamp(ts) {
    return moment(ts).fromNow();
  }
}

AccountDetail.title = 'Detail';

export default AccountDetail;
