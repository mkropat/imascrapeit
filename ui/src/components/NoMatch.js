import React from 'react';

class NoMatch extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <p className="text-center">That page isn't here</p>
    )
  }
}

NoMatch.title = 'Not Found';

export default NoMatch;
