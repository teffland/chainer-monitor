import React, { Component } from 'react'
import {connect} from 'react-redux'
import {XYPlot, XAxis, YAxis, HorizontalGridLines, LineSeries} from 'react-vis';
import CollapsibleCard from './CollapsibleCard'
import ScalarPlot from './ScalarPlot'
import MonitoredVariableReport from './MonitoredVariableReport'

import {getExperiment} from '../actions'


class ExperimentSummary extends Component {
  componentDidMount() {
    if (!this.props.loaded) {
      this.props.dispatch(getExperiment(this.props.name))
    }
  }

  secondsToString(seconds) {
    var numdays = Math.floor(seconds / 86400);
    var numhours = Math.floor((seconds % 86400) / 3600);
    var numminutes = Math.floor(((seconds % 86400) % 3600) / 60);
    var numseconds = Math.round(((seconds % 86400) % 3600) % 60);
    return numdays + " days " + numhours + " hours " + numminutes + " minutes " + numseconds + " seconds";
  }

  finishTiming() {
    return this.props.finish_time ? (
        <div className="row">
          <div className="col-sm-2"><b>Start Time:</b></div>
          <div className="col-sm-10"><samp>  {this.props.start_time}</samp></div>
          <div className="col-sm-2"><b>Finish Time:</b></div>
          <div className="col-sm-10"><samp>  {this.props.finish_time}</samp></div>
          <div className="col-sm-2"><b>Elapsed Time:</b></div>
          <div className="col-sm-10"><samp>  {this.secondsToString(this.props.elapsed_time)}</samp></div>
        </div>
      ):(
        <div className="row">
          <div className="col-sm-2"><b>Start Time:</b></div>
          <div className="col-sm-10"><samp>  {this.props.start_time}</samp></div>
          <div className="col-sm-2"><b>Elapsed Time:</b></div>
          <div className="col-sm-10"><samp>  {this.secondsToString(this.props.elapsed_time)}</samp></div>
          <div className="col-sm-2"><b>Estimated Total Time:</b></div>
          <div className="col-sm-10"><samp>  {this.secondsToString(this.props.estimated_total_time)}</samp></div>
          <div className="col-sm-2"><b>Estimated Time Left:</b></div>
          <div className="col-sm-10"><samp>  {this.secondsToString(this.props.estimated_total_time - this.props.elapsed_time)}</samp></div>
        </div>
      )
  }

  scalarPlots() {
    let plots = []
    // console.log('Scalars', this.props.scalars)
    for (let key in this.props.scalars) {
      plots.push(
        <CollapsibleCard title={key} h={5}>
          <ScalarPlot
            key={key}
            title={key}
            xTitle={"Epoch"}
            yTitle={key}
            data={this.props.scalars[key]}
          />
        </CollapsibleCard>)
    }
    return plots
  }

  monitoredVarReports() {
    let reports = []
    for (let key in this.props.monitoredVars) {
      let data = this.props.monitoredVars[key]
      // console.log('data', data)
      reports.push(
        <CollapsibleCard title={key} h={5}>
          <MonitoredVariableReport
            key={key}
            title={key}
            data={this.props.monitoredVars[key]}
          />
        </CollapsibleCard>)
    }
    return reports
  }

  render() {
    console.log('experiment props', this.props)
    return (
      <CollapsibleCard title={this.props.task+': '+this.props.title} disabled={!this.props.loaded}
        loading={this.props.loading} loadingError={this.props.loadingError}>
        <h6 className="card-subtitle mb-3 text-muted">{this.props.name}</h6>
        <h6 className="card-subtitle mb-3">{this.props.description}</h6>

        {this.finishTiming()}

        <CollapsibleCard title={"Setup Details"} h={5}>
          <CollapsibleCard title={"Launch Details"} h={5}>
            <div className="card-text">
              <div className="row">
                <div className="col-sm-12"><b>Output Directory:</b>
                  <samp>  {this.props.cwd}/{this.props.results_dirname}</samp>
                </div>
              </div>
              <div className="row">
                <div className="col-sm-6"><b>Host:</b><samp>  {this.props.hostname}</samp></div>
              </div>
              <div className="row">
                <div className="col-sm-6"><b>PID:</b><samp>  {this.props.pid}</samp></div>
              </div>
            </div>
          </CollapsibleCard>
          <CollapsibleCard title={"Data Setup Details"} h={5}>
            <div className="card-text">
              <pre>{JSON.stringify(this.props.data_setup.setup_config, null, 2) }</pre>
            </div>
          </CollapsibleCard>
          <CollapsibleCard title={"Model Setup Details"} h={5}>
            <div className="card-text">
              <pre>{JSON.stringify(this.props.model_setup.setup_config, null, 2) }</pre>
            </div>
          </CollapsibleCard>
          <CollapsibleCard title={"Trainer Setup Details"} h={5}>
            <div className="card-text">
              <pre>{JSON.stringify(this.props.trainer_setup.setup_config, null, 2) }</pre>
            </div>
          </CollapsibleCard>
        </CollapsibleCard>

        <CollapsibleCard title={"Scalars"} h={5}>
          {this.scalarPlots()}
        </CollapsibleCard>

        <CollapsibleCard title={"Monitored Variables"} h={5}>
          {this.monitoredVarReports()}
        </CollapsibleCard>
      </CollapsibleCard>
    )
  }
}


// class ExperimentSummary extends Component {
//   toggleHidden() {
//     console.log('toggle called')
//     this.props.dispatch((() => {
//       return {
//         type: "TOGGLE_HIDDEN",
//         name: this.props.name
//         }
//     })())
//   }
//
//   toggleHiddenSetup(setupName) {
//     this.props.dispatch((() => {
//       return {
//         type: "TOGGLE_HIDDEN_SETUP",
//         name: this.props.name,
//         setupName: setupName
//         }
//     })())
//   }
//
//   componentDidMount() {
//     if (!this.props.loaded) {
//       this.props.dispatch(getExperiment(this.props.name))
//     }
//   }
//
//   styles() {
//     return {
//       cardStyle: {padding: '0px', marginBottom:'10px'},
//       titleStyle: {margin: '0px'}
//     }
//   }
//
//   render() {
//     const hidden = this.props.hidden
//     const style = this.styles()
//     const loadingSpinner = this.props.loading ? (
//       <span>
//         &emsp;<i className="fa fa-spinner fa-spin fa fa-fw"></i>
//       </span>
//     ):(null)
//
//     const loadingErrorBadge = this.props.loadingError ? (
//       <span>&emsp;<span className="badge badge-danger">Loading Error</span></span>
//     ):(null)
//
//     const detailButton = this.props.hidden ? (
//       <button type="button" className="btn btn-secondary float-right"
//         onClick={this.toggleHidden.bind(this)}
//         disabled={!this.props.loaded}>
//         <i className="fa fa-chevron-down" aria-hidden="true"></i>
//       </button>
//     ):(
//       <button type="button" className="btn btn-secondary float-right"
//         onClick={this.toggleHidden.bind(this)}>
//         <div className="float-right">
//           <i className="fa fa-chevron-up" aria-hidden="true"></i>
//         </div>
//       </button>
//     )
//
//     // const dataSetupDetailButton = null
//     const dataSetupDetailButton = this.props.loaded && this.props.data_setup.hidden ? (
//       <button type="button" className="btn btn-secondary float-right"
//         onClick={this.toggleHiddenSetup.bind(this, 'data_setup')}>
//         <div className="float-right">
//           <i className="fa fa-chevron-down" aria-hidden="true"></i>
//         </div>
//       </button>
//     ):(
//       <button type="button" className="btn btn-secondary float-right"
//         onClick={this.toggleHiddenSetup.bind(this, 'data_setup')}>
//         <div className="float-right">
//           <i className="fa fa-chevron-up" aria-hidden="true"></i>
//         </div>
//       </button>
//     )
//
//     const modelSetupDetailButton = this.props.loaded && this.props.model_setup.hidden ? (
//       <button type="button" className="btn btn-secondary float-right"
//         onClick={this.toggleHiddenSetup.bind(this, 'model_setup')}>
//         <div className="float-right">
//           <i className="fa fa-chevron-down" aria-hidden="true"></i>
//         </div>
//       </button>
//     ):(
//       <button type="button" className="btn btn-secondary float-right"
//         onClick={this.toggleHiddenSetup.bind(this, 'model_setup')}>
//         <div className="float-right">
//           <i className="fa fa-chevron-up" aria-hidden="true"></i>
//         </div>
//       </button>
//     )
//
//     const trainerSetupDetailButton = this.props.loaded && this.props.trainer_setup.hidden ? (
//       <button type="button" className="btn btn-secondary float-right"
//         onClick={this.toggleHiddenSetup.bind(this, 'trainer_setup')}>
//         <div className="float-right">
//           <i className="fa fa-chevron-down" aria-hidden="true"></i>
//         </div>
//       </button>
//     ):(
//       <button type="button" className="btn btn-secondary float-right"
//         onClick={this.toggleHiddenSetup.bind(this, 'trainer_setup')}>
//         <div className="float-right">
//           <i className="fa fa-chevron-up" aria-hidden="true"></i>
//         </div>
//       </button>
//     )
//     console.log('experiment props', name)
//     console.log(this.props)
//     return (
//       <div className="card col-sm-12" style={style.cardStyle}>
//           <div className="card-header">
//             <h4 className="card-title" style={style.titleStyle}>
//               {this.props.title} {loadingSpinner} {loadingErrorBadge} {detailButton}
//             </h4>
//           </div>
//           { !this.props.hidden &&
//             <div className="card-block">
//               <h6 className="card-subtitle mb-2 text-muted">{this.props.name}</h6>
//               {/* <h6 className="card-subtitle mb-2 text-muted">Here's some data</h6> */}
//               {/* <p>{JSON.stringify(this.props)}</p> */}
//               <div className="card-block">
//                 <h4 className="card-title">Data Setup {dataSetupDetailButton}</h4>
//                 { !this.props.data_setup.hidden &&
//                   <div className="card-text">
//                     <pre>{JSON.stringify(this.props.data_setup.setup_config, null, 2) }</pre>
//                   </div>
//                 }
//               {/* </div> */}
//               {/* <div className="card-block"> */}
//                 <h4 className="card-title">Model Setup {modelSetupDetailButton}</h4>
//                 { !this.props.model_setup.hidden &&
//                   <div className="card-text">
//                     <pre>{JSON.stringify(this.props.model_setup.setup_config, null, 2) }</pre>
//                   </div>
//                 }
//               {/* </div> */}
//               {/* <div className="card-block"> */}
//                 <h4 className="card-title">Trainer Setup {trainerSetupDetailButton}</h4>
//                 { !this.props.trainer_setup.hidden &&
//                   <div className="card-text">
//                     <pre>{JSON.stringify(this.props.trainer_setup.setup_config, null, 2) }</pre>
//                   </div>
//                 }
//               </div>
//               <div className="card-block">
//                 <V.VictoryChart domainPadding={20}
//                   height={200}
//                   // padding={10}
//                   // containerComponent={
//                   //   <V.VictoryBrushContainer dimension="x" selectedDomain={{x: [0.1, 0.3]}}/>
//                   // }
//                   // theme={plotTheme}
//                 >
//                   <V.VictoryAxis dependentAxis tickCount={5}/>
//                   <V.VictoryAxis tickCount={10}/>
//
//                 <V.VictoryLine data={this.props.log}
//                   style={{
//                     data: {stroke: "tomato", opacity: 0.7},
//                     labels: {fontSize: 12},
//                     parent: {border: "1px solid #ccc"}
//                   }}
//                   labels={d => d['main/loss']}
//                   labelComponent={<V.VictoryTooltip/>}
//                   x="iteration" y="main/loss"/>
//                 </V.VictoryChart>
//
//                 {/* <V.VictoryChart domainPadding={20}
//                   height={200}
//                 >
//                 <V.VictoryLine data={this.props.log}
//                   style={{
//                     data: {stroke: "tomato", opacity: 0.7},
//                     labels: {fontSize: 12},
//                     parent: {border: "1px solid #ccc"}
//                   }}
//                   x="iteration" y="main/accuracy"/>
//                 <V.VictoryLine data={this.props.log}
//                   style={{
//                     data: {stroke: "steelblue", opacity: 0.7},
//                     labels: {fontSize: 12},
//                     parent: {border: "1px solid #ccc"}
//                   }}
//                   x="iteration" y="validation/main/accuracy"/>
//                 </V.VictoryChart>*/}
//               </div>
//             </div>
//           }
//         </div>
//     )
//   }
// }

export default connect((state, ownProps) => {
  return {...state.experiments.name2data[ownProps.name], ...state}
})(ExperimentSummary)
