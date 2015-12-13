import React from 'react';
import { Link } from 'react-router'

class Home extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Link to="/accounts">
        Go to Accounts
      </Link>
    );
  }
}

Home.title = 'Home';

export default Home;
