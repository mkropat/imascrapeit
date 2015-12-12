window.jQuery = window.$ = require('jquery/dist/jquery.min');
require('bootstrap-webpack');

import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Route } from 'react-router'

import App from './Main';
import Accounts from './Accounts';
import Login from './Login';
import NoMatch from './NoMatch';
import Setup from './Setup';

// Render the main component into the dom
//ReactDOM.render(<App />, document.getElementById('app'));
ReactDOM.render((
  <Router>
    <Route path="/" component={App}>
      <Route path="setup" component={Setup} />
      <Route path="login" component={Login} />
      <Route path="accounts" component={Accounts} />
      <Route path="*" component={NoMatch} />
    </Route>
  </Router>
), document.getElementById('app'))
