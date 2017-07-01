import initialState from '../initialState'

export default (state, action) => {
  state = {...initialState.window, ...state}
  switch (action.type) {
    case 'WINDOW_RESIZE':
      state.width = action.width
      state.height = action.height
      return state
    default:
      return state
  }
}
