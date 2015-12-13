window.jQuery = window.$ = require('jquery/dist/jquery.min');
require('bootstrap-webpack');

import React from 'react';
import ReactDOM from 'react-dom';
import { IndexRoute, Router, Route } from 'react-router'

import AccountDetail from './AccountDetail';
import Accounts from './Accounts';
import AccountsResource from '../data/AccountsResource';
import AddAccount from './AddAccount';
import App from './Main';
import Home from './Home';
import Login from './Login';
import NoMatch from './NoMatch';
import Notifier from '../services/Notifier';
import Setup from './Setup';

let accountsResource = new AccountsResource();
let breadcrumbNotifier = new Notifier();

ReactDOM.render((
  <Router>
    <Route path="/" component={App} breadcrumbNotifier={breadcrumbNotifier}>
      <IndexRoute component={Home} />
      <Route path="setup" component={Setup} />
      <Route path="login" component={Login} />
      <Route path="accounts" component={Accounts} accountsResource={accountsResource}>
        <Route path="new" component={AddAccount} accountsResource={accountsResource} />
        <Route path=":id" component={AccountDetail}
          accountsResource={accountsResource}
          breadcrumbNotifier={breadcrumbNotifier} />
      </Route>
      <Route path="*" component={NoMatch} />
    </Route>
  </Router>
), document.getElementById('app'))
