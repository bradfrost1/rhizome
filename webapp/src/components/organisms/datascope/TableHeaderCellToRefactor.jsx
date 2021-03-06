import _ from 'lodash'
import React from 'react'

var TableHeaderCellToRefactor = React.createClass({
    displayName: 'TableHeaderCellToRefactor',

    propTypes: {
        schema: React.PropTypes.shape({
            name: React.PropTypes.string,
            title: React.PropTypes.string
        }), // schema for this field
        field: React.PropTypes.object,
        title: React.PropTypes.string, // to override schema title
        onClick: React.PropTypes.func, // usually the sort function
        isSortedBy: React.PropTypes.bool, // true if the table is sorted by this column
        sortIndicatorAscending: React.PropTypes.string,
        sortIndicatorDescending: React.PropTypes.string
    },
    getDefaultProps: function getDefaultProps() {
        return {
            onClick: null,
            sortIndicatorAscending: ' ▲',
            sortIndicatorDescending: ' ▼'
        };
    },
    _getTitle: function _getTitle() {
        return _.isUndefined(this.props.title) ? this.props.field.title : this.props.title;
    },
    render: function render() {
        var isSortAscending = (this.props.sortOrder || '').toLowerCase().indexOf('asc') === 0;
        var sortIndicator = this.props.isSortedBy ? isSortAscending ? this.props.sortIndicatorAscending : this.props.sortIndicatorDescending : '';

        return React.createElement(
            'th',
            { className: 'ds-data-table-col-head', onClick: this.props.onClick },
            React.createElement(
                'span',
                { className: 'ds-data-table-col-title' },
                this._getTitle()
            ),
            React.createElement(
                'span',
                { className: 'ds-data-table-sort-indicator' },
                sortIndicator
            )
        );
    }
});

export default TableHeaderCellToRefactor
