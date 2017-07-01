import initialState from '../initialState'

export default (state, action) => {
  state = {...initialState.experiments, ...state}
  switch (action.type) {
    case 'GET_NAMES_FETCH':
      state.fetching = true
      return state
    case 'GET_NAMES_SUCCESS':
      state.fetched = true
      state.fetching = false
      state.fetchError = false
      action.names.forEach((name) => {
        if (!(name in state.name2data)) {
          state.names.push(name)
          state.name2data[name] = {
            loading: false,
            loaded: false,
            loadingError: false,
            log:[],
            data_setup:{loading:true},
            model_setup:{loading:true},
            trainer_setup:{loading:true}
          }
        }
      })
      return state
    case 'GET_NAMES_FAILURE':
      state.fetched = false
      state.fetchError = true
      return state
    case 'GET_EXPERIMENT_FETCH':
      if (!(action.name in state.name2data)
          || !state.name2data[action.name].loaded) {
        state.name2data[action.name].loading = true
      }
      return state
    case 'GET_EXPERIMENT_SUCCESS':
      console.log('get experiment',action)
      var data = state.name2data[action.name]
      data = { ...data,
               ...action.json.config,
               log: action.json.log,
               scalars: action.json.scalars,
               monitoredVars:action.json.monitored_vars,
               ...action.json.timing }
      data.loading = false
      data.loaded = true
      state.name2data[action.name] = data
      return state
    case 'GET_EXPERIMENT_FAILURE':
      state.name2data[action.name].loading = false
      state.name2data[action.name].loadingError = true
      return state
    default:
      return state
  }
}
