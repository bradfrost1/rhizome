'use strict';

var React = require('react/addons');
var Vue = require('vue');

var LandingPage      = require('view/LandingPage.jsx');
var DashboardList = require('view/dashboard-list/DashboardList.jsx');
var DashboardBuilder = require('view/dashboard-builder/DashboardBuilder.jsx');
var Navigation       = require('component/Navigation.jsx');
var AdminApp         = require('./ufadmin');
var GroupForm = require('view/group-form/GroupForm.jsx');

Vue.config.debug = true;

Vue.component('vue-dropdown', require('./component/dropdown'));
Vue.component('vue-table', require('./component/table'));
Vue.component('vue-table-editable', require('./component/table-editable'));
Vue.component('vue-pagination', require('./component/pagination'));
Vue.component('vue-tooltip', require('./component/tooltip'));
Vue.component('vue-menu', require('./component/menu'));

Vue.filter('num', require('./filter/num'));

Vue.partial('tooltip-stacked-bar', require('./partial/tooltip-stacked-bar.html'));
Vue.partial('tooltip-heatmap', require('./partial/tooltip-heatmap.html'));
Vue.partial('tooltip-indicator', require('./partial/tooltip-indicator.html'));

React.render(
	React.createElement(Navigation),
	document.getElementById('main-nav')
);

module.exports = {
	Explorer: function (el) {
		new Vue({
			el: el,
			components: { 'uf-explorer': require('./view/explorer') }
		});
	},
	Dashboard: function (el) {
		React.render(React.createElement(require('view/Dashboard.jsx')), el);
	},
	DataEntry: function (el) {
		new Vue({
			el: el,
			components: { 'uf-entry-form': require('./view/entry-form') }
		});
	},
	FieldMapping: function (el,document_id) {
		new Vue({
			el: el,
			components: { 'uf-field-mapping': require('./view/field-mapping') },
			data:{'document_id':document_id}
		});
	},
	UserAccount: function (el,user_id) {
		new Vue({
			el: el,
			components: { 'uf-user-account': require('./view/user-account') },
			data:{'user_id':user_id}
		});
	},
	LandingPage: function (el) {
		React.render(React.createElement(LandingPage), el);
	},
	DashboardList: function (el) {
		React.render(React.createElement(DashboardList), el);
	},
	DashboardBuilder: function (el) {
		React.render(React.createElement(DashboardBuilder), el);
	},
	ChartBuilder: function (el) {
		var ChartBuilder = require('view/chart-builder/ChartBuilder.jsx');
		React.render(React.createElement(ChartBuilder), el);
	},
	UFAdmin: function(el) {
		AdminApp.render(document.getElementById('main'));
	},
	GroupForm: function(el) {
		React.render(React.createElement(GroupForm), el);
		// React.render(React.createElement(GroupForm, {group_id: group_id}), el);
	}
};
