'use strict';

var _      = require('lodash');
var d3     = require('d3');
var moment = require('moment');

var column  = require('./renderer/column');
var data    = require('util/data');
var label   = require('./renderer/label');
var palette = require('colors/coolgray');

// Color palette from I Want Hue
// var palette = [
// "#6094BA",
// "#699CA7",

// "#B6DAE5",
// "#589EE4",
// "#3CA6A9",
// "#909A92",

// "#D5D5C6",
// "#90D7D0",
// "#5CB3DE",
// "#A2B6C8",
// "#D2F2EA",
// "#8ED0E9"];

module.exports = {
	replace  : true,
	template : require('./bar.html'),

	paramAttributes : [
		'data-facet',
		'data-format-string',
		'data-x',
		'data-x-label'
	],

	mixins : [
		require('./mixin/resize'),
		require('./mixin/margin')
	],

	data : function () {
		return {
			chartType    : 'column',
			facet        : 'indicator.id',
			formatString : 's',
			series       : [],
			xLabel       : 'MMM [’]YY'
		};
	},

	computed : {
		colWidth : function () {
			return Math.floor(this.contentWidth / d3.max(this.series, function (s) {
				return s.values.length;
			})) - 1;
		},

		empty : function () {
			return !this.series || !this.series.length;
		},

		getX : function () {
			var x = this.x;

			if (_.isString(x)) {
				x = data.accessor(x);
			}

			return x;
		},

		labels : function () {
			var self = this;
			var fmt  = d3.format(this.formatString);

			return _(this.series)
				.map(function (s) {
					return _.assign({ name : s.name },
						_.max(s.values, function (d) { return d.campaign.start_date; }));
				})
				.map(function (d) {
					return {
						text    : d.name + ' ' + fmt(d.value),
						x       : self.xScale(self.getX(d)) + self.colWidth,
						y       : self.yScale(d.y0 + d.y),
						defined : data.defined(d.value)
					};
				})
				.reverse()
				.value();
		},

		xScale : function () {
			var domain = _(this.series)
				.pluck('values')
				.flatten()
				.map(this.getX)
				.uniq()
				.sortBy()
				.value();

			return d3.scale.ordinal()
				.domain(domain)
				.rangeBands([0, this.contentWidth], 0.1, 0);
		},

		yScale : function () {
			return d3.scale.linear()
				.domain([0, _(this.series)
					.pluck('values')
					.flatten()
					.map(function (d) {
						return d.y + d.y0;
					})
					.max()])
				.range([this.contentHeight, 0]);
		}
	},

	methods : {
		draw : function () {
			var svg = d3.select(this.$$.svg);

			var x      = this.getX;
			var xScale = this.xScale;
			var yScale = this.yScale;
			var width  = xScale.rangeBand();

			var series = svg.select('.data').selectAll('.series')
				.data(this.series, function (d) { return d.name; });

			var color = d3.scale.ordinal().range(palette);

			series.enter()
				.append('g')
				.attr('class', 'series');

			series
				.style('fill', function (d) { return color(d.name); })
				.call(column()
					.values(function (series) { return series.values; })
					.height(function (d) { return yScale(d.y0) - yScale(d.y0 + d.y); })
					.width(width)
					.x(function (d) { return xScale(x(d)); })
					.y(function (d) { return yScale(d.y0 + d.y); })
				);

			series.exit().remove();

			series.selectAll('rect')
				.on('mouseover', this.onMouseOver)
				.on('mouseout', this.onMouseOut);

			var fmt = d3.format(this.formatString);

			svg.select('.annotation').selectAll('.series.label')
				.data(this.labels)
				.call(label()
					.addClass('series')
					.width(this.contentWidth)
					.height(this.contentHeight)
					.align(false));

			var t = svg.transition().duration(500);

			var self = this;

			t.select('.x.axis')
				.call(d3.svg.axis()
					.orient('bottom')
					.tickSize(0)
					.tickPadding(4)
					.tickValues(_.filter(xScale.domain(), function (d, i, domain) {
						// Include every fourth tick value unless that tick is within three
						// ticks of the last value. Always include the last tick. We have to
						// do this manually because D3 ignores the ticks() value for
						// ordinal scales
						return (i % 4 === 0 && i + 3 < domain.length) || (i + 1) === domain.length;
					}))
					.tickFormat(function (d) {
						return moment(d).format(self.xLabel);
					})
					.scale(xScale));

			t.select('.y.axis')
				.call(d3.svg.axis()
					.orient('right')
					.tickFormat(fmt)
					.tickSize(this.contentWidth)
					.ticks(3)
					.scale(yScale));

			svg.selectAll('.y.axis text')
				.attr({
					'dx' : -this.contentWidth,
					'dy' : -4
				});
		},

		onMouseOver : function (d) {
			var x      = this.getX;
			var xScale = this.xScale;
			var yScale = this.yScale;
			var fmt    = d3.format(this.formatString);

			var target = x(d);

			if (target === this._currentHover) {
				return;
			}

			var labels = _(this.series)
				.map(function (s) {
					return _.assign({ name : s.name },
						_(s.values)
							.filter(function (d) {
								return d.campaign.start_date.getTime() === target;
							})
							.first());
				})
				.map(function (d) {
					return {
						text    : d.name + ' ' + fmt(d.value),
						x       : xScale(x(d)),
						y       : yScale(d.y0 + d.y),
						defined : data.defined(d.value)
					};
				})
				.reverse()
				.value();

			var svg = d3.select(this.$$.svg);

			svg.select('.annotation')
				.selectAll('.series.label')
				.data(labels)
				.call(label()
					.addClass('series')
					.width(this.contentWidth)
					.height(this.contentHeight)
					.align(true));

			svg.select('.data')
				.selectAll('rect')
				.transition()
				.duration(300)
				.style('opacity', function (d) {
					return x(d) === target ? 1 : 0.3;
				});
		},

		onMouseOut : function () {
			var svg = d3.select(this.$$.svg);

			this._currentHover = null;

			svg.select('.annotation')
				.selectAll('.series.label')
				.data(this.labels)
				.call(label()
					.addClass('series')
					.width(this.contentWidth)
					.height(this.contentHeight)
					.align(false));

			svg.select('.data')
				.selectAll('rect')
				.transition()
				.duration(300)
				.style('opacity', 1);
		}
	},

	watch : {
		'series' : 'draw',
		'height' : 'draw',
		'width'  : 'draw',
	}
};
