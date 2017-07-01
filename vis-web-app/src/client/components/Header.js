import React, { Component } from 'react'
import { IndexLink, Link } from 'react-router'
import { connect } from 'react-redux'

class Header extends Component {
  render() {
    const brand = this.props.brand,
          links = this.props.links,
          style = { height:`${this.props.height}px` }
    return (
      <div className="header">
        <nav className="navbar navbar-toggleable-sm navbar-inverse bg-primary" style={style}>
         <button className="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>
        {/* <nav className="navbar navbar-inverse bg-primary" style={style}> */}
          <IndexLink className="navbar-brand" to="/">
            {brand}
          </IndexLink>
          <div className="collapse navbar-collapse" id="navbarSupportedContent">
          {/* <div id="navbarSupportedContent"> */}
            <ul className="navbar-nav mr-auto">
              {links.map((link, i) => {
                if (!i) {
                  return (
                    <li className="nav-item">
                      <IndexLink className="nav-link" activeClassName="active"
                        key={`link-${i}`} to={link.to}>
                        {link.text}
                      </IndexLink>
                    </li>
                  )
                }
                else {
                  return (
                  <li className="nav-item">
                    <Link className="nav-link" activeClassName="active"
                      key={`link-${i}`} to={link.to}>
                      {link.text}
                    </Link>
                  </li>
                  )
                }
              })}
            </ul>
            {/* <form class="form-inline my-2 my-lg-0">
              <input class="form-control mr-sm-2" type="text" placeholder="Search">
              <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
            </form> */}
          </div>
        </nav>
      </div>
    )
  }
}

export default connect(
  (state) => {
    return {
      height: state.window.headerHeight,
      brand: state.window.headerBrand,
      links: state.window.headerLinks
    }
  },
  null, null,
  { pure: false }
)(Header)
