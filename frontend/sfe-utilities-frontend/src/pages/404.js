import React, { Component } from 'react';
import './../App.css';

class PageNotFoundPage extends Component {
  render() {
    return (
      <div>
        <h1>404 » Page Not Found :((</h1>
        Maybe try going to <a href="/">the home page</a>.
      </div>
    );
  }
}

export default PageNotFoundPage;
