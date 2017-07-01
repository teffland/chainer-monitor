import React from 'react'
import { Route, IndexRoute } from 'react-router'
import App from './components/App'
import HomeView from './components/HomeView'
import ComparisonView from './components/ComparisonView'

export default (
  <Route path="/" component={App}>
    <IndexRoute component={HomeView} />
    {/* <IndexRoute component={FrontPage} /> */}
    <Route path="/home" component={HomeView} />
    <Route path="/compare" component={ComparisonView} />
  </Route>
)
