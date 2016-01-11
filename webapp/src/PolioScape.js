import React from 'react'
import Vue from 'vue'

import DashboardNav from 'component/DashboardNav.jsx'
import DashboardList from 'view/dashboard-list/DashboardList.jsx'
import AdminApp from './ufadmin'
import CampaignsPage from './ufadmin/CampaignsPage.js'
import HomepageChartsView from 'view/HomepageChartsView.jsx'

Vue.config.debug = true

Vue.component('vue-dropdown', require('./component/dropdown'))
Vue.component('vue-table', require('./component/table'))
Vue.component('vue-table-editable', require('./component/table-editable'))
Vue.component('vue-tooltip', require('./component/vue-tooltip'))
Vue.component('vue-menu', require('./component/vue-menu'))

Vue.filter('num', require('./util/format').num)

Vue.partial('tooltip-stacked-bar', require('./partial/tooltip-stacked-bar.html'))
Vue.partial('tooltip-heatmap', require('./partial/tooltip-heatmap.html'))
Vue.partial('tooltip-indicator', require('./partial/tooltip-indicator.html'))

React.render(
  React.createElement(DashboardNav),
  document.getElementById('dashboards-nav')
)

export default {
  Explorer: function (el) {
    React.render(React.createElement(require('view/Explorer.jsx')), el)
  },
  Dashboard: function (el) {
    React.render(React.createElement(require('view/Dashboard.jsx')), el)
  },
  DataEntry: function (el) {
    React.render(React.createElement(require('view/entry-form/EntryForm.jsx')), el)
  },
  SourceData: function (el) {
    var SourceData = require('view/SourceData.jsx')
    React.render(React.createElement(SourceData), el)
  },
  UserAccount: function (el, userId) {
    let UserAccount = require('view/user-account/UserAccount.jsx')
    React.render(React.createElement(UserAccount, {userId: userId}), el)
  },
  DashboardList: function (el) {
    React.render(React.createElement(DashboardList), el)
  },
  HomepageCharts: function (el) {
    React.render(React.createElement(HomepageChartsView), el)
  },
  DashboardBuilder: function (el, dashboardId) {
    var DashboardBuilder = require('view/dashboard-builder/DashboardBuilder.jsx')
    React.render(React.createElement(DashboardBuilder, { dashboardId: dashboardId }), el)
  },
  UFAdmin: function (el) {
    AdminApp.render(document.getElementById('main'))
  },
  CampaignsPage: function (id_start_date, id_end_date) {
    CampaignsPage.render(id_start_date, id_end_date)
  }
}
