'use strict';

var _  = require('lodash');
var d3 = require('d3');

var CHARTS = {
	BulletChart : require('./bullet')
};

var DEFAULTS = {
	margin : {
		top    : 0,
		right  : 0,
		bottom : 0,
		left   : 0
	}
}

function ChartFactory(type, el, data, options) {
	if (!_.isFunction(CHARTS[type])) {
		throw new Error(type + ' is not a valid chart type');
	}

	_.defaults(CHARTS[type].prototype, ChartFactory.prototype);

	var chart = new CHARTS[type]();
	chart.initialize(el, data, options);

	return chart;
}

ChartFactory.prototype.initialize = function (el, data, options) {
	options = this._options = _.defaults({}, options, this.defaults, DEFAULTS);

	this._height = _.get(options, 'height', el.clientHeight);
	this._width  = _.get(options, 'width', el.clientWidth);

	var svg = this._svg = d3.select(el).append('svg')
		.attr('viewBox', '0 0 ' + this._width + ' ' + this._height);

	var h = this._height - options.margin.top - options.margin.bottom;

	var g = svg.append('g')
		.attr('transform', 'translate(' + options.margin.left + ',' +
			options.margin.top + ')');

	g.append('g').attr('class', 'y axis');
	g.append('g').attr({
		'class'     : 'x axis',
		'transform' : 'translate(0,' + h + ')'
	});
	g.append('g').attr('class', 'data');
	g.append('g').attr('class', 'annotation');
};

module.exports = ChartFactory;
