'use strict';

var _     = require('lodash');
var React = require('react');
var api = require('data/api.js')
var moment = require('moment');
var page = require('page');

var NavigationStore     = require('stores/NavigationStore');
var ReviewTable = require('dashboard/sd/ReviewTable.js');
var DocOverview = require('dashboard/sd/DocOverview.js');

var TitleMenu  = require('component/TitleMenu.jsx');
var MenuItem    = require('component/MenuItem.jsx');

var {
	Datascope, LocalDatascope,
	SimpleDataTable, SimpleDataTableColumn,
	Paginator, SearchBar,
	FilterPanel, FilterDateRange
	} = require('react-datascope');

var SourceDataDashboard = React.createClass({
  propTypes : {
    dashboard : React.PropTypes.object.isRequired,
    data      : React.PropTypes.object.isRequired,
    region    : React.PropTypes.object.isRequired,
		doc_id    : React.PropTypes.number.isRequired,
		doc_tab    : React.PropTypes.string.isRequired,

    loading   : React.PropTypes.bool
  },


	getInitialState : function () {
    return {
      regions      : [],
      campaigns    : [],
      region       : null,
      campaign     : null,
      dashboard    : null,
      doc_id    	 : -1,
			doc_tab    	 : 'mapping',
    };
  },

  getDefaultProps : function () {
    return {
      loading : false
    };
  },

  render : function () {
    var loading = this.props.loading;
		var campaign = this.props.campaign;
		var region = this.props.region;
		var loading = this.props.loading;
		var doc_id = this.state.doc_id;
		var doc_tab = this.props.doc_tab

		var docItems = MenuItem.fromArray(
			_.map(NavigationStore.documents, d => {
				return {
					title : d.docfile,
					value : d.id
				};
			}),
			this._setDocId);

		var doc_tabs = MenuItem.fromArray(
			_.map(['overview','mapping','validate','results'], d => {
				return {
					title : d,
					value : d
				};
			}),
			this._setDocTab);

		var doc_tab = 'mapping'//this.state.doc_tab

		// navigation to set doc-id and doc-processor //
		var review_nav =
		<div className="admin-container">
			<h1 className="admin-header"></h1>
			<div className="row">
				document_id: <TitleMenu text={doc_id}>
					{docItems}
				</TitleMenu>
			</div>
			<div className="row">
			<TitleMenu text={'validate'}>
				{doc_tabs}
			</TitleMenu>
			</div>
		</div>;

		const fields = {
			map_link: {
				title: 'Master Object Name',
				key: 'id',
				renderer: (id) => {
						return MapButtonFunction(id)
					}
			},
		};


		const fieldNamesOnTable = {'mapping':['id','content_type','source_object_code','master_object_id']}//];

		var table_key = _.kebabCase(this.props.region.name) + this.props.campaign.slug + this.doc_id;
		// data table //
		var review_table = <ReviewTable
					title='sample title'
					getMetadata={api.admin.docMapMeta}
					getData={api.admin.docMap}
					region={region}
					key={table_key}
					>
					<Paginator />
					<SimpleDataTable>
						{fieldNamesOnTable[doc_tab].map(fieldName => {
							return <SimpleDataTableColumn name={fieldName} />
						})}
					</SimpleDataTable>
			</ReviewTable>

		var review_breakdown = <DocOverview
			loading={loading}
			doc_id={doc_id}
			>
		</DocOverview>

		var tab_title = 'Mapping For document_id: ' + doc_id

		return (
					<div className="row">
					<div className="medium-9 columns">
					<h2 style={{ textAlign: 'right' }} className="ufadmin-page-heading">{tab_title}</h2>
					{review_table}
					</div>
					<div className="medium-3 columns">
						{review_nav}
						{review_breakdown}
					</div>
		</div>);;
  },

_setDocId : function (doc_id) {
	console.log('loading_new_document_id')
	console.log(doc_id)
	this._navigate({ doc_id : doc_id });
	this.state.doc_id = doc_id
	this.forceUpdate();
},

_setDocTab : function (doc_tab) {
	console.log('loading_new_doc_tabd')
	console.log(doc_tab)
	this._navigate({ doc_tab : doc_tab });
	this.state.doc_tab = doc_tab
	this.forceUpdate();
	},

_navigate : function (params) {
	var slug     = _.get(params, 'dashboard', _.kebabCase(this.props.dashboard.title));
	var region   = _.get(params, 'region', this.props.region.name);
	var campaign = _.get(params, 'campaign', moment(this.props.campaign.start_date, 'YYYY-MM-DD').format('YYYY/MM'));
	var doc_id = _.get(params, 'doc_id', this.state.doc_id);

	if (_.isNumber(region)) {
		region = _.find(this.state.regions, r => r.id === region).name;
	}
	console.log('NAVIGATING')
  page('/datapoints/' + [slug, region, campaign].join('/') + '#' + doc_id);
},


});

module.exports = SourceDataDashboard;
