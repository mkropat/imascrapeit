require('normalize.css');
require('styles/App.css');

import React from 'react';
import axios from 'axios';
import { Link } from 'react-router'

class AppComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      session: null
    };
  }

  componentWillMount() {
    axios.get('/api/session')
      .then(r => {
        let session = r.data || {};
        this.props.history.push(getStateFromSession(session));
      });
  }

  render() {
    let breadcrumbs = this.props.routes.slice(0, this.props.routes.length - 1);
    let active = this.props.routes[this.props.routes.length - 1];

    return (
      <div className="index container">
        <ol className="breadcrumb">
          {breadcrumbs.map((item, index) =>
            <li key={index}>
              <Link to={item.path || ''}>
                {item.component.title}
              </Link>
            </li>
          )}
          <li className="active">
            {active.component.title}
          </li>
        </ol>

        {this.props.children}
      </div>
    );
  }
}

AppComponent.title = "I'ma Scrape It"

function getStateFromSession(session) {
  if (!session.is_setup) {
    return '/init';
  }
  else if (!session.is_authenticated) {
    return '/login';
  }
  else {
    return '/accounts';
  }
}

export default AppComponent;
