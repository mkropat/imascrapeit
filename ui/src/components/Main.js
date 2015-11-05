require('normalize.css');
require('styles/App.css');

import React from 'react';

import api from './api';

let yeomanImage = require('../images/yeoman.png');

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
    api.get('/session')
      .then(r => {
        let session = r || {};
        this.props.history.pushState(null, getStateFromSession(session));
      });
  }

  render() {
    let session = this.state.session || {};

    return (
      <div className="index">
        <img src={yeomanImage} alt="Yeoman Generator" />

        {this.props.children}
      </div>
    );
  }
}

AppComponent.defaultProps = {
};

export default AppComponent;
