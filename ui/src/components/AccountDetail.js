import React from 'react';
import { Link } from 'react-router'

class AccountDetail extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      account: {}
    };
  }

  componentWillMount() {
    this.props.route.accountsResource.get(this.props.params.id)
      .then(r => {
        this.setState({
          account: r
        });

        this.props.route.breadcrumbNotifier.notify(AccountDetail, r.id);
      });
  }

  render() {
    return (
      <div className="container">
        <h2>Detail</h2>
        <p>{this.state.account.id}</p>
      </div>
    );
  }
}

AccountDetail.title = 'Detail';

export default AccountDetail;
