import { Component } from 'react';
import Routes from './routes'
import './App.css';

class App extends Component {
  render() {
    return this.getPageForRoute(window.location.pathname);
  }

  getPageForRoute(route){
    for (var r in Routes){
      if (route === Routes[r].location && Routes[r].component){
        return Routes[r].component.render()
      }
    }
    
    return Routes.PAGE_NOT_FOUND.component.render();
  }
}

export default App;
