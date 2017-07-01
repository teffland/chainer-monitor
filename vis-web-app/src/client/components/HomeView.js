import React, {Component} from 'react'
import {connect} from 'react-redux'
import ExperimentSummary from './ExperimentSummary'
import { getNames } from '../actions'

class HomeView extends Component {
  // constructor(props) {
  //   super(props)
  //   this.props.dispatch(getNames())
  // }
  componentDidMount() {
    this.props.dispatch(getNames())
  }

  render() {
    var summaries, loadingSpinner, errorBadge;
    if (Object.keys(this.props.names).length > 0) {
      summaries = this.props.names.map((name, i) => {
        return<ExperimentSummary key={`summary-${i}`} name={name}/>
      })
    } else {
      summaries = <p>There are no experiments to view yet.</p>
    }

    if (this.props.fetching) {
      loadingSpinner = <div className="text-center" style={{width:'100%'}}>
                        &emsp;<i className="fa fa-spinner fa-spin fa-2x fa-fw"></i>
                      </div>
    }

    if (this.props.fetchError) {
      errorBadge = <span>&emsp;<span className="badge badge-danger">Loading Error</span></span>
    }

    return (
      <div>
        <div className="row">
            <h2>Experiments Overview {errorBadge}</h2>
        </div>
        {loadingSpinner}
        {this.props.fetched &&
          <div className="row">
              {summaries}
          </div>
        }
    </div>
    )

  }
}

export default connect((state) => {
  return { ...state.experiments }
})(HomeView)
