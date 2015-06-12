'use strict';

var _     = require('lodash');
var React = require('react');

var ChartFactory = require('chart');

module.exports = React.createClass({
  propTypes : {
    data    : React.PropTypes.array.isRequired,
    type    : React.PropTypes.string.isRequired,

    id      : React.PropTypes.string,
    options : React.PropTypes.object,
    loading : React.PropTypes.bool
  },

  getDefaultProps : function () {
    return {
      loading : false
    };
  },

  render : function () {
    var loading;

    if (this.props.loading) {
      loading = (
        <div className='overlay'>
          <div>
            <div>
              <i class="fa fa-spinner" v-class="fa-spin: loading"></i>
              &ensp;Loading
            </div>
          </div>
        </div>
      );
    }

    return (
      <div id={this.props.id} className={'chart ' + _.kebabCase(this.props.type)}>
        {loading}
      </div>
    );
  },

  componentDidMount : function () {
    this._chart = ChartFactory(
      this.props.type,
      React.findDOMNode(this),
      this.props.data,
      this.props.options);
  },

  componentWillReceiveProps: function(nextProps) {
  	if(nextProps.type != this.props.type)
  	{
  	    React.findDOMNode(this).innerHTML = '';
  		this._chart = ChartFactory(
  		    nextProps.type,
  		    React.findDOMNode(this),
  		    this.props.data,
  		    this.props.options);
  	}
  },

  componentDidUpdate : function () {
    this._chart.update(this.props.data, this.props.options);
  }
});
