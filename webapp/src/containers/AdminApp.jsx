import React from 'react'
import Router from 'react-router'

import SimpleForm from 'components/organisms/manage-system/SimpleForm'
import CampaignsContainer from 'containers/CampaignsContainer'

var {Route, RouteHandler, Link} = Router
var AdminApp = React.createClass({
  contextTypes: {
    router: React.PropTypes.func
  },

  render: function () {
    var q_params = this.context.router.getCurrentParams()

    return <div className='admin-container'>
      <ul className='admin-nav'>
        <li><Link to='manage' params={{'id': q_params['id'], 'contentType': 'indicator'}} >Manage Indicators</Link></li>
        <li><Link to='manage' params={{'id': q_params['id'], 'contentType': 'indicator_tag'}} >Manage Tags</Link></li>
        <li><Link to='users'>Users</Link></li>
        <li><Link to='locations'>Locations</Link></li>
        <li><Link to='campaigns'>Campaigns</Link></li>
        <li><Link to='indicators'>Indicators</Link></li>
        <li><Link to='tags'>Tags</Link></li>
        <li><Link to='tags-tree'>Tags-Tree</Link></li>
      </ul>
      <RouteHandler/>
    </div>
  }
})

var routes = (
    <Route name='app' path='/manage_system/' handler={AdminApp}>
      <Route name='manage' path='/manage_system/manage/:contentType/:id?' handler={SimpleForm}/>
      <Route name='updateCampaign' path='/campaign/:id?' handler={CampaignsContainer}/>
      <Route name='users' handler={require('components/organisms/manage-system/UsersAdmin')} />
      <Route name='locations' handler={require('components/organisms/manage-system/LocationAdmin')} />
      <Route name='campaigns' handler={require('components/organisms/manage-system/CampaignsAdmin')} />
      <Route name='indicators' handler={require('components/organisms/manage-system/IndicatorsAdmin')} />
      <Route name='tags' handler={require('components/organisms/manage-system/TagsAdmin')} />
      <Route name='tags-tree' handler={require('components/organisms/manage-system/TagsTreeAdmin')} />
  </Route>
)

export default {
  render: function (container) {
    Router.run(routes, Router.HistoryLocation, Handler => {
      React.render(<Handler />, container)
    })
  }
}
