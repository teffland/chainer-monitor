import { combineReducers } from 'redux'
import { routerReducer } from 'react-router-redux'
import windowReducer from './window'
import experimentsReducer from './experiments'
import plotsReducer from './plots'

const rootReducer = combineReducers({
    routing: routerReducer,
    /* your reducers */
    window: windowReducer,
    experiments: experimentsReducer,
    plots: plotsReducer
})

export default rootReducer
