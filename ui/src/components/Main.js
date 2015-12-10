require('normalize.css');
require('styles/App.css');

import React from 'react';
import axios from 'axios';

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
    let session = this.state.session || {};

    return (
      <div className="index">
        {this.props.children}
      </div>
    );
  }
}

AppComponent.defaultProps = {
};

export default AppComponent;
