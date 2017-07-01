import { createStore, applyMiddleware } from 'redux'
import thunk from 'redux-thunk'
import logger from 'redux-logger'
import rootReducer from './reducers';

const middleware = applyMiddleware(thunk, logger)
const setupStore = (initialState) => {
  return createStore(
          rootReducer,
          initialState,
          middleware
        )
}
export default setupStore
