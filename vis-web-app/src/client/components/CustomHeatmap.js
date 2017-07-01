import React, { Component } from 'react'
import {XYPlot, XAxis, YAxis, HorizontalGridLines, VerticalGridLines, Hint} from 'react-vis';
import {HeatmapSeries} from 'react-vis'
import {scaleLinear} from "d3-scale";

class CustomHeatmap extends Component {
  constructor(props) {
    super(props)
    // reformat the input datastructure for react-vis
    // we abuse their heatmap and display it literally since it's precomputed
    console.log('heatmap props', props)
    let max = props.hist.reduce((maxVal, datum) => {
      return Math.max(maxVal, datum.histVals.reduce((a,b) => Math.max(a,b)))
    }, 0)
    // console.log('max param hist val', max)
    let colorScale = scaleLinear()
      .domain([0, max])
      .range(['white', 'blue'])
    let data = props.hist.reduce((data, datum) => {
      for (let j in datum.histVals) {
        data.push({
          x:datum.iteration,
          y:Number(j),
          color:colorScale(datum.histVals[j])
        })
      }
      return data
    }, [])
    console.log('heatmap data', data)
    // data = [
    //   {x:0,y:0, color:'#eee'},
    //   {x:0,y:1, color:'#000'},
    //   {x:1,y:1, color:'#eee'},
    //   {x:1,y:0, color:'#000'},
    // ]

    console.log('max y', data.reduce((val,d)=> Math.max(val, d.y), 0))

    this.state = {width:300, height:400, data:data,
      histEdges:props.hist[0].histEdges}
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
          margin={{left: 80, right: 10, top: 10, bottom: 40}}
          >
          <HeatmapSeries
            colorType="literal"
            data={this.state.data}/>
          <HorizontalGridLines
            tickValues={[...Array(this.state.histEdges.length).keys()].map(d => d-.5)}
            style={{
              stroke:'lightgrey'
            }}/>
          <VerticalGridLines
            style={{
              stroke:'lightgrey'
            }}
            tickValues={this.props.hist.reduce((outArray, d) => {
              //  console.log(d)
               if (d.epoch % 1 == 0) {
                 outArray.push(d.epoch+.5)
               }
               return outArray
             }, [])}/>
          <XAxis title={"Epoch"}
            style={{
              line:{stroke:'lightgrey'}
            }}
            tickValues={this.props.hist.reduce((outArray, d) => {
              //  console.log(d)
               if (d.epoch % 1 == 0) {
                 outArray.push(d.epoch+.5)
               }
               return outArray
             }, [])}/>
          <YAxis
            style={{
              line:{stroke:'lightgrey'}
            }}
            tickValues={[...Array(this.state.histEdges.length).keys()].map(d => d-.5)}
            tickFormat={tickVal => this.state.histEdges[Number(tickVal+.5)].toExponential()}
          />
        </XYPlot>
      </div>
    )
  }
}

CustomHeatmap.defaultProps = {}

export default CustomHeatmap
