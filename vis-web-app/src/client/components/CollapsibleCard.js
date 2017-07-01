import React, { Component } from 'react'

export default class CollapsibleCard extends Component {
  constructor(props) {
    super(props)
    this.state = {hidden: true}
  }

  toggleHidden() {
    this.setState(oldState => {
      return {...oldState, hidden:!oldState.hidden}
    })
  }

  loadingSpinner() {
    return this.props.loading ? (
      <span>
        &emsp;<i className="fa fa-spinner fa-spin fa fa-fw"></i>
      </span>
    ):(null)
  }

  loadingErrorBadge() {
    return this.props.loadingError ? (
      <span>&emsp;<span className="badge badge-danger">Loading Error</span></span>
    ):(null)
  }

  detailButton() {
    const detailButton = this.state.hidden ? (
      <button type="button" className="btn btn-secondary float-right"
        onClick={this.toggleHidden.bind(this)}
        disabled={this.props.disabled}>
        <i className="fa fa-chevron-down" aria-hidden="true"></i>
      </button>
    ):(
      <button type="button" className="btn btn-secondary float-right"
        onClick={this.toggleHidden.bind(this)}>
        <div className="float-right">
          <i className="fa fa-chevron-up" aria-hidden="true"></i>
        </div>
      </button>
    )
    return detailButton
  }

  styles() {
    return {
      cardStyle: {padding: '0px', marginTop:'10px'},
      titleStyle: {margin: '0px'}
    }
  }

  render() {
    let style = this.styles()
    const H = `h${this.props.h || 3}`

    return (
      <div className="card col-sm-12" style={style.cardStyle}>
        <div className="card-header">
          <H className="card-title" style={style.titleStyle}>
            {this.props.title} {this.loadingSpinner()} {this.loadingErrorBadge()} {this.detailButton()}
          </H>
        </div>
      { !this.state.hidden &&
        <div className="card-block">
          {this.props.children}
        </div>
      }
      </div>
    )
  }
}
