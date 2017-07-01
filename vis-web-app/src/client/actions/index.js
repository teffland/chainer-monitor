export const getNames = () => {
  return (dispatch) => {
    dispatch({ type:'GET_NAMES_FETCH' })
    fetch('api/experiment-names', {
      method: 'get',
      headers: {'Content-Type': 'application/json'}
    }).then((response) => {
      response.json().then((json) => {
        dispatch({
          type: 'GET_NAMES_SUCCESS',
          names: json
        })
      })
    }).catch((error) => {
      dispatch({
        type: 'GET_NAMES_FAILURE'
      })
    })
  }
}

export const getExperiment = (name) => {
  return (dispatch) => {
    console.log(`get experiment action ${name}`)
    dispatch({ type:'GET_EXPERIMENT_FETCH', name:name})
    fetch(`api/experiment/${name}`, {
      method: 'get',
      headers: {'Content-Type': 'application/json'}
    }).then((response) => {
      response.json().then((json) => {
        dispatch({
          type: 'GET_EXPERIMENT_SUCCESS',
          name: name,
          json: json
        })
      }).catch((error) => {
        dispatch({
          type: 'GET_EXPERIMENT_FAILURE',
          name: name
        })
      })
    }).catch((error) => {
      dispatch({
        type: 'GET_EXPERIMENT_FAILURE',
        name: name
      })
    })
  }
}

export const toggleHidden = (uid) => {
  return {
    type: 'TOGGLE_HIDDEN',
    uid: uid
  }
}
