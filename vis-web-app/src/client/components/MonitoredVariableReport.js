import React, { Component } from 'react'
import ScalarPlot from './ScalarPlot'
import CustomHeatmap from './CustomHeatmap'
/**
* TODO:
* [ ] - Allow for multiple plots
* [ ] - Show the iteration and epoch ticks for x axis
* [ ] - Have dynamic crosshair show values
*/
class MonitoredVariableReport extends Component {
  constructor(props) {
    super(props)
    this.state = {width:300, height:400, active:'params'}
  }

  componentDidMount() {
    this.setState({width:this.refs.child.parentNode.getBoundingClientRect().width-20})
  }

  setActive(name) {
    this.setState({active:name})
  }

  styles() {
    return {
      cardStyle: {padding: '0px', marginTop:'10px'},
      titleStyle: {margin: '0px'}
    }
  }

  subPlot() {
    if (this.state.active == 'updates') {
      // return <ScalarPlot
      //   title={""}
      //   xTitle={"Epoch"}
      //   yTitle={"Gradient:Param Ratio"}
      //   data={this.props.data.map(d => {
      //     return {
      //       epoch:d.epoch,
      //       iteration:d.iteration,
      //       y:d.updates.mean
      //     }
      //   })}
      // />
      let edges = this.props.data[0].updates.histEdges
      return <CustomHeatmap key='update-heatmap' hist={this.props.data.map(d => {
        return {
          epoch:d.epoch,
          iteration:d.iteration,
          histVals:d.updates.histVals,
          histEdges:edges
        }
      })}/>
    } else if (this.state.active == 'params') {
      let edges = this.props.data[0].params.histEdges
      console.log('p data',this.props.data)
      return <CustomHeatmap key='param-heatmap' hist={this.props.data.map(d => {
        return {
          epoch:d.epoch,
          iteration:d.iteration,
          histVals:d.params.histVals,
          histEdges:edges
        }
      })}/>
    } else {
      let edges = this.props.data[0].grads.histEdges
      return <CustomHeatmap key='grad-heatmap' hist={this.props.data.map(d => {
        return {
          epoch:d.epoch,
          iteration:d.iteration,
          histVals:d.grads.histVals,
          histEdges:edges
        }
      })}/>
    }
  }

  render() {
    let style = this.styles()
    const H = `h${this.props.h || 3}`
    let active = this.state.active
    console.log('var report props', this.props)
    console.log(this.props.data[0].params != null)
    // console.log('active', active)
    // console.log("nav-link" + (active=='params' ? " active":""))
    return (
      <div ref="child">
        <ul className="nav nav-pills nav-justified">
          {this.props.data[0].params != null &&
            <li className="nav-item">
              <a className={"nav-link" + (active=='params' ? " active":"")}
                onClick={() => this.setActive('params')}>Parameters</a>
            </li>}
          {this.props.data[0].grads != null &&
            <li className="nav-item">
              <a className={"nav-link" + (active=='grads' ? " active":"")}
                onClick={() => this.setActive('grads')}>Gradients</a>
            </li>}
          {this.props.data[0].updates != null &&
            <li className="nav-item">
              <a className={"nav-link" + (active=='updates' ? " active":"")}
                onClick={() => this.setActive('updates')}>Update Ratio</a>
            </li>}
        </ul>
        {this.subPlot()}
      </div>
    )
  }
}

MonitoredVariableReport.defaultProps = {
  title: "Sample Scalar Plot",
  data: [ {x:0, y:0}, {x:1, y:.5}, {x:2, y:2} ],
  xTitle: "Sample X",
  yTitle: "Sample y",
  // width: 400,
  // height: 300,
  lineColor: 'orange',
  lineOpacity: 1.
}

export default MonitoredVariableReport
