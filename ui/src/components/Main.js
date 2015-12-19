require('normalize.css');
require('styles/App.css');

import React from 'react';
import axios from 'axios';
import { Link } from 'react-router'

class AppComponent extends React.Component {
  constructor(props) {
    super(props);

    this._listenCanceler = null;

    this.state = {
      breadcrumbTitles: {}
    };
  }

  componentWillMount() {
    this._listenCancler = this.props.route.breadcrumbNotifier.listen(
        this.updateBreadcrumbTitles.bind(this));

    //axios.get('/api/session')
    //  .then(r => {
    //    let session = r.data || {};
    //    this.props.history.push(getStateFromSession(session));
    //  });
  }

  updateBreadcrumbTitles(component, title) {
    let newBreadcrumbTitles = Object.assign({}, this.state.breadcrumbTitles);
    newBreadcrumbTitles[component] = title;

    this.setState({
      breadcrumbTitles: newBreadcrumbTitles
    });
  }

  render() {
    let breadcrumbs = this.getBreadcrumbs();
    let active = breadcrumbs.pop();

    return (
      <div className="index container">
        <ol className="breadcrumb">
          {breadcrumbs.map((item, index) =>
            <li key={index}>
              <Link to={item.path || ''}>
                {item.title}
              </Link>
            </li>
          )}
          <li className="active">
            {active.title}
          </li>
        </ol>

        {this.props.children}
      </div>
    );
  }

  getBreadcrumbs() {
    let parts = this.props.routes.map(i => ({
      path: i.path,
      title: this.getTitle(i.component)
    }));

    let lastPath = '';
    parts.forEach(i => {
      i.path = (lastPath + '/' + i.path).replace('//', '/');
      lastPath = i.path;
    });

    return parts;
  }

  getTitle(component) {
    return this.state.breadcrumbTitles.hasOwnProperty(component)
        ? this.state.breadcrumbTitles[component]
        : component.title
  }

  componentWillUnmount() {
    if (this._listenCancler) {
      this._listenCancler();
    }
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
