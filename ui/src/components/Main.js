require('normalize.css');
require('styles/App.css');

import React from 'react';

let yeomanImage = require('../images/yeoman.png');

class AppComponent extends React.Component {
  render() {
    return (

      <div className="index">
        <img src={yeomanImage} alt="Yeoman Generator" />

        <div className="notice">
          <label>Username <input type="text" id="username" /></label>
          <label>Password <input type="text" id="password" /></label>
        </div>
      </div>
    );
  }
}

AppComponent.defaultProps = {
};

export default AppComponent;
