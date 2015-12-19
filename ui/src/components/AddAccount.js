import React from 'react';
import axios from 'axios';
import { Link } from 'react-router'

class AddAccount extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      drivers: [],
      isAdding: false,
      driver: '',
      name: '',
      username: '',
      password: '',
      addLink: null
    };
  }

  componentWillMount() {
    this.props.route.accountsResource.list()
      .then(r => {
        this.setState({
          addLink: r.data._links.add
        });
      });

    axios.get('/api/drivers')
      .then(r => {
        this.setState({
          drivers: r.data.drivers
        });
      });
  }

  updateField(evt) {
    let newState = {};
    newState[evt.target.id] = evt.target.value;
    this.setState(newState);
  }

  render() {
    let drivers = this.state.drivers.map(d =>
      <option key={d.id} value={d.id}>{d.id} ({d.entry_point})</option>
    );

    return (
      <div className="container">
        <h2>Add Account</h2>
        <form onSubmit={this.addAccount.bind(this)}>
          <div className="form-group">
            <label htmlFor="driver">Driver</label>
            <select id="driver" className="form-control" onChange={this.updateField.bind(this)} value={this.state.driver}>
              <option>Select</option>
              {drivers}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="name">Account Name</label>
            <input className="form-control" id="name" placeholder="Name" onChange={this.updateField.bind(this)} value={this.state.name} />
          </div>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input className="form-control" id="username" placeholder="Username" onChange={this.updateField.bind(this)} value={this.state.username} />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input type="password" className="form-control" id="password" placeholder="Password" onChange={this.updateField.bind(this)} value={this.state.password} />
          </div>

          <button type="submit"
            className="btn btn-primary"
            disabled={this.canAdd() ? '' : 'disabled'}>
            {this.state.isAdding ? 'Adding...' : 'Add'}
          </button>
          <Link to="/accounts" className="btn btn-link">Cancel</Link>
        </form>
      </div>
    );
  }

  canAdd() {
    return this.state.addLink && !this.state.isAdding;
  }

  addAccount(evt) {
    evt.preventDefault();

    this.setState({
      isAdding: true
    });

    let link = this.state.addLink;
    let data = {
      action: 'create',
      name: this.state.name,
      driver: this.state.driver,
      username: this.state.username,
      password: this.state.password
    };
    this.props.route.accountsResource.actionTillComplete(link.method, link.href, data)
      .then(r => {
        this.props.history.push('/accounts');
      });
  }
}

AddAccount.title = 'Add';

export default AddAccount;
