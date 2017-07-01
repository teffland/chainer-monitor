import React, { Component } from 'react'
import { Link } from 'react-router'
import {connect} from 'react-redux'

class Footer extends Component {
  render() {
    const textStyle = {
      position: 'relative',
      color: 'black',
      backgroundColor: 'white',/*'#cde7fe',*/
      height: `${this.props.height}px`,
      lineHeight: `${this.props.height}px`
    }
    return (
      <div className="footer">
        <div className="footer-text" style={textStyle}>
          <div className="text-center">Made with ♥, Tom Effland 2017</div>
        </div>
      </div>
    )
  }
}

export default connect((state) => {
  return { height:state.window.footerHeight }
})(Footer)
