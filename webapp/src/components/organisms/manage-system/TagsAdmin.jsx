import React from 'react'

import api from 'utilities/api'

import SimpleDataTableColumn from 'components/organisms/datascope/SimpleDataTableColumn'
import Paginator from 'components/organisms/datascope/Paginator'
import SearchBar from 'components/organisms/datascope/SearchBar'

import AdminPage from 'components/organisms/manage-system/AdminPage'
import TableToRefactor from 'components/organisms/datascope/TableToRefactor'

const fields = {
  edit_link: {
    title: 'Edit',
    key: 'id',
    renderer: (id) => {
      return <a href={`/manage_system/manage/indicator_tag/${id}`}>Edit Tags</a>
    }
  },
  id: { title: 'ID', name: 'id' },
  tag_name: { title: 'Tag Name', name: 'tag_name' },
  parent_tag_id: { title: 'Parent Tag Id', name: 'parent_tag_id' },
  parent_tag__tag_name: { title: 'Parent Tag Name', name: 'parent_tag__tag_name' }
}

const fieldNamesOnTable = ['id', 'tag_name', 'parent_tag_id', 'parent_tag__tag_name', 'edit_link']

var TagsAdmin = React.createClass({
  render () {
    var datascopeFilters = (
      <div>
        <SearchBar
          placeholder='Search tags ...'
          fieldNames={fieldNamesOnTable}
          />
      </div>
    )

    return (
      <AdminPage
        title='Tags'
        getData={api.get_indicator_tag}
        datascopeFilters={datascopeFilters}
        fields={fields} >
        <Paginator />
          <TableToRefactor>
            {fieldNamesOnTable.map(fieldName => {
              return <SimpleDataTableColumn name={fieldName} />
            })}
          </TableToRefactor>
      </AdminPage>
    )
  }
})

export default TagsAdmin
