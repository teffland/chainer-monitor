import React, { Component } from 'react'
import {connect} from 'react-redux'
import Header from './Header'
import Footer from './Footer'

class App extends Component {
  screenResize() {
    const resizeAction = () => {
      return {
        type: 'WINDOW_RESIZE',
        width: window.innerWidth,
        height: window.innerHeight
      }
    }
    this.props.dispatch(resizeAction())
  }

  constructor(props) {
    super(props)
    this.screenResize()
  }
  componentDidMount() {
    window.addEventListener('resize', this.screenResize.bind(this))
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this.screenResize.bind(this))
  }
  render() {
    const height = this.props.height - (this.props.headerHeight + this.props.footerHeight),
          style = {
            backgroundColor:'#d9d9d9',
            minHeight: `${height}px`,
            padding: '15px 0px 0px 0px',
            overflow: 'scroll'
          }
    return (
      <div>
        <Header/>
        <div style={style}>
          <div className="container">
            <div className="row">
              <div className="col">
                {this.props.children}
              </div>
            </div>
          </div>
        </div>
        <Footer/>
      </div>
    )
  }
}
export default connect((state) => {return state.window})(App)
