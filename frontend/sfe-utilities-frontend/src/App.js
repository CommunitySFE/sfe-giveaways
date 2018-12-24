import React, { Component } from 'react';
import PageNotFoundPage from './pages/404.js';
import './App.css';

class App extends Component {
  render() {
    return this.getPageForRoute(window.location.pathname);
  }

  getPageForRoute(route){
    if (route === "/") {
      return (<div className="mainbody mx-3 my-3">
          <h1>Server Dashboard</h1>
        </div>);
    } else {
      return (new PageNotFoundPage()).render();
    }
  }
}

export default App;
