import _ from 'lodash'
import React from 'react/addons'
import InterfaceMixin from 'utilities/InterfaceMixin'

let SearchBar = React.createClass({
  displayName: 'SearchBar',

  mixins: [InterfaceMixin('Datascope', 'DatascopeSearch')],
  propTypes: {
    onChangeSearch: React.PropTypes.func, // required
    id: React.PropTypes.oneOfType([React.PropTypes.string, React.PropTypes.number]),
    fieldNames: React.PropTypes.array,
    value: React.PropTypes.string
  },

  getDefaultProps () {
    return { id: 'searchbar' } // pass unique id to have multiple independent search bars within one Datascope
  },

  onChangeSearch (e) {
    this.props.onChangeSearch(this.props.id, e.target.value, this.props.fieldNames)
  },

  render () {
    let propsToPass = _.noop({ type: 'text',
                               value: this.props.value,
                               onChange: this.onChangeSearch
                              },
                              _.omit(this.props, ['id', 'fieldNames', 'value', 'onChangeSearch']))
    return (
        <div>
          <input type={'text'} value={this.props.value} onChange={this.onChangeSearch} {...propsToPass}/>
        </div>
      )
  }
})
// let _extends =
//   Object.assign || function (target) {
//      for (let i = 1; i < arguments.length; i++) {
//        let source = arguments[i] for (let key in source)
//        { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key] } } } return target
//    }

export default SearchBar
