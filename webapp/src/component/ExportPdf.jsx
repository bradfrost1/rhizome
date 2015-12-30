import React from 'react'

var ExportPdf = React.createClass({
  propTypes: {
    className: React.PropTypes.string
  },

  defaults: {
    label: 'Export PDF',
    isFetching: false,
    url: '/datapoints/dashboards/export_pdf/?path=',
    interval: 1000,
    cookieName: 'pdfDownloadToken'
  },

  getInitialState () {
    return this.defaults
  },

  _getCookie (name) {
    if (document.cookie.length > 0) {
      var c_start = document.cookie.indexOf(name + '=')
      if (c_start !== -1) {
        c_start = c_start + name.length + 1
        var c_end = document.cookie.indexOf(';', c_start)
        if (c_end === -1) {
          c_end = document.cookie.length
        }
        return document.cookie.substring(c_start, c_end)
      }
    }
    return ''
  },

  _onExportDashboard () {
    this.setState({
      label: 'Fetching...',
      isFetching: true,
      href: this.state.url + window.location.href
    })
    var self = this
    var refreshIntervalId = window.setInterval(() => {
      var cookieValue = self._getCookie(self.state.cookieName)
      if (cookieValue === 'true') {
        this._isCompleteExportDashboard(refreshIntervalId)
      }
    }, this.state.interval)
  },

  _isCompleteExportDashboard (refreshIntervalId) {
    this.setState({
      label: 'Export PDF',
      isFetching: false,
      href: 'about:blank'
    })
    document.cookie = this.state.cookieName + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;'
    window.clearInterval(refreshIntervalId)
  },

  render () {
    return (
      <div className='dropdown-list cd-titlebar-margin'>
        <a className={this.props.className} onClick={this._onExportDashboard} disabled={this.state.isFetching}>
          {this.state.label}
        </a>
        <iframe width='0' height='0' className='hidden' src={this.state.href}></iframe>
      </div>
    )
  }
})

export default ExportPdf
