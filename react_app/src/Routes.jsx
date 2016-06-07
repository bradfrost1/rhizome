import React from 'react'
import { Route } from 'react-router'

import BasePageContainer from 'containers/BasePageContainer'

import CampaignsPage from 'components/pages/campaigns/CampaignsPage'
import CampaignPage from 'components/pages/campaigns/CampaignPage'
import CampaignEditPage from 'components/pages/campaigns/CampaignEditPage'

import ChartsPage from 'components/pages/charts/ChartsPage'
import ChartPage from 'components/pages/charts/ChartPage'
import ChartEditPage from 'components/pages/charts/ChartEditPage'

import IndicatorsPage from 'components/pages/indicators/IndicatorsPage'
import IndicatorPage from 'components/pages/indicators/IndicatorPage'
import IndicatorEditPage from 'components/pages/indicators/IndicatorEditPage'

import LocationsPage from 'components/pages/locations/LocationsPage'
import LocationPage from 'components/pages/locations/LocationPage'
import LocationEditPage from 'components/pages/locations/LocationEditPage'

import SourceDatasPage from 'components/pages/source_data/SourceDatasPage'
import SourceDataPage from 'components/pages/source_data/SourceDataPage'
import SourceDataEditPage from 'components/pages/source_data/SourceDataEditPage'

import UsersPage from 'components/pages/users/UsersPage'
import UserPage from 'components/pages/users/UserPage'
import UserEditPage from 'components/pages/users/UserEditPage'

import AboutPage from 'components/pages/info/AboutPage'
import BugReportPage from 'components/pages/info/BugReportPage'
import ContactPage from 'components/pages/info/ContactPage'
import SitemapPage from 'components/pages/info/SitemapPage'

import EnterDataPageContainer from 'containers/EnterDataPageContainer'
import ManageSystemPage from 'components/pages/ManageSystemPage'

const Routes = (
	<Route path="/react_app" component={BasePageContainer}>

		// RESOURCE ROUTES
		//---------------------------------------------------------
	  <Route path="/react_app/campaigns" component={CampaignsPage}/>
	  <Route path="/react_app/campaigns/:campaign_id" component={CampaignPage}/>
	  <Route path="/react_app/campaigns/:campaign_id/edit" component={CampaignEditPage}/>

	  <Route path="/react_app/new_charts" component={ChartsPage}/>
	  <Route path="/react_app/new_charts/:chart_id" component={ChartPage}/>
	  <Route path="/react_app/new_charts/:chart_id/edit" component={ChartEditPage}/>

	  <Route path="/react_app/indicators" component={IndicatorsPage}/>
	  <Route path="/react_app/indicators/:indicator_id" component={IndicatorPage}/>
	  <Route path="/react_app/indicators/:indicator_id/edit" component={IndicatorEditPage}/>

	  <Route path="/react_app/locations" component={LocationsPage}/>
	  <Route path="/react_app/locations/:location_id" component={LocationPage}/>
	  <Route path="/react_app/locations/:location_id/edit" component={LocationEditPage}/>

	  <Route path="/react_app/source_data" component={SourceDatasPage}/>
	  <Route path="/react_app/source_data/:source_data_id" component={SourceDataPage}/>
	  <Route path="/react_app/source_data/:source_data_id/edit" component={SourceDataEditPage}/>

	  <Route path="/react_app/users" component={UsersPage}/>
	  <Route path="/react_app/users/:user_id" component={UserPage}/>
	  <Route path="/react_app/users/:user_id/edit" component={UserEditPage}/>

		// INFO ROUTES
		//---------------------------------------------------------
	  <Route path="/react_app/about" component={AboutPage}/>
	  <Route path="/react_app/bug_report" component={BugReportPage}/>
	  <Route path="/react_app/contact" component={ContactPage}/>
	  <Route path="/react_app/sitemap" component={SitemapPage}/>

		// OTHER ROUTES
		//---------------------------------------------------------
	  <Route path="/react_app/enter_data" component={EnterDataPageContainer}/>
	  <Route path="/react_app/manage_system" component={ManageSystemPage}/>
	</Route>
)

export default Routes