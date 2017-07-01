import React, { Component } from 'react'
import {XYPlot, XAxis, YAxis, HorizontalGridLines, LineSeries, Hint} from 'react-vis';

/**
* TODO:
* [ ] - Allow for multiple plots
* [ ] - Show the iteration and epoch ticks for x axis
* [ ] - Have dynamic crosshair show values
*/
class ScalarPlot extends Component {
  constructor(props) {
    super(props)
    this.state = {width:300, height:400}
  }

  componentDidMount() {
    this.setState({width:this.refs.child.parentNode.getBoundingClientRect().width-20})
    // console.log('parent width', this.refs.child.parentNode.getBoundingClientRect().width)
    // console.log('my width', this.state.width)
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
    console.log('state', this.state)
    return (
      <div ref="child" style={{marginTop:'10px', marginBottom:'10px'}}>
        {/* <div className='text-center'>
          <H>{this.props.title}</H>
        </div> */}
        <XYPlot
          width={this.state.width}
          height={this.state.height}
          yPadding={30}
          margin={{left: 80, right: 10, top: 10, bottom: 40}}
          >
          <HorizontalGridLines
            style={{
              stroke:'lightgrey'
            }}/>
          <LineSeries
            style={{fill:'none'}}
            data={this.props.data.map(d => {return {x:d.iteration, y:d.y}})}
            color={this.props.lineColor}
            opacity={this.props.lineOpacity}
          />
          <XAxis title={this.props.xTitle}
            style={{
              line:{stroke:'lightgrey'}
            }}
            tickValues={this.props.data.reduce((outArray, d) => {
              //  console.log(d)
               if (d.epoch % 1 == 0) {
                 outArray.push(d.epoch)
               }
               return outArray
             }, [])}
           tickTotal={5}/>

          <YAxis title={this.props.yTitle}/>
        </XYPlot>
      </div>
    )
  }
}

ScalarPlot.defaultProps = {
  title: "Sample Scalar Plot",
  data: [ {x:0, y:0}, {x:1, y:.5}, {x:2, y:2} ],
  xTitle: "Sample X",
  yTitle: "Sample y",
  // width: 400,
  // height: 300,
  lineColor: 'orange',
  lineOpacity: 1.
}

export default ScalarPlot
