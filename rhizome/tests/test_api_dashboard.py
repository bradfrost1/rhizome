from tastypie.test import ResourceTestCase
from django.contrib.auth.models import User
from rhizome.models import CustomDashboard, CustomChart, LocationPermission,\
    Location, LocationType, Office, ChartToDashboard

import json

class DashboardResourceTest(ResourceTestCase):
    def setUp(self):
        super(DashboardResourceTest, self).setUp()

        # Create a user.
        self.username = 'john'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username,
                                             'john@john.com', self.password)

        self.lt = LocationType.objects.create(name='test',admin_level = 0)
        self.o = Office.objects.create(name = 'Earth')

        self.top_lvl_location = Location.objects.create(
                name = 'Nigeria',
                location_code = 'Nigeria',
                location_type_id = self.lt.id,
                office_id = self.o.id,
            )

        LocationPermission.objects.create(user_id = self.user.id,\
            top_lvl_location_id = self.top_lvl_location.id)

        self.get_credentials()

        # create their api_key

    def get_credentials(self):
        result = self.api_client.client.login(username=self.username,
                                              password=self.password)
        return result

    def test_dashboard_post(self):
        post_data = {'title': 'the dashboard title'}
        CustomDashboard.objects.all().delete()
        self.assertEqual(CustomDashboard.objects.count(), 0)

        resp = self.api_client.post('/api/v1/custom_dashboard/', format='json', \
                                    data=post_data, authentication=self.get_credentials())
        response_data = self.deserialize(resp)

        self.assertHttpCreated(resp)
        self.assertEqual(post_data['title'], response_data['title'])
        self.assertEqual(CustomDashboard.objects.count(), 1)

    def test_dashboard_post_rows(self):        
        dboard_title = 'the dashboard title'
        dboard_rows = json.dumps([{'charts':['fdfdf'], 'layout':1}, {'charts':['ddsds'], 'layout':2}])
        post_data = {
        'title': dboard_title,
        'rows' : dboard_rows
        }
        resp = self.api_client.post('/api/v1/custom_dashboard/', format='json', \
                                    data=post_data, authentication=self.get_credentials())
        self.assertHttpCreated(resp)
        response_data = self.deserialize(resp)
        self.assertEqual(CustomDashboard.objects.count(), 1)
        dboard = CustomDashboard.objects.get(title = dboard_title)
        self.assertEqual(json.dumps(dboard.rows), dboard_rows)

    def test_dashboard_post_no_params(self):
        resp = self.api_client.post('/api/v1/custom_dashboard/', format='json', \
                                    data={}, authentication=self.get_credentials())
        self.assertHttpApplicationError(resp)

    def test_dashboard_chart_post(self):

        ## create two charts ##
        c1 = CustomChart.objects.create(uuid = 'a',title = 'a',chart_json = '')
        c2 = CustomChart.objects.create(uuid = 'b',title = 'b',chart_json = '')

        dashboard_title = '2 Chart Dashboard'
        chart_uuids = '%s,%s'%(c1.uuid, c2.uuid)
        post_data = {
            'title': dashboard_title,
            'chart_uuids': chart_uuids
            }

        ## post the dashboard title and the associated charts to the API ##
        resp = self.api_client.post('/api/v1/custom_dashboard/',\
            format='json',\
            data=post_data,\
            authentication=self.get_credentials()\
        )

        response_data = self.deserialize(resp)

        ## find the uuids that have been created in association with the dash ##
        db_chart_uuids = CustomChart.objects\
            .filter(charttodashboard__dashboard_id = response_data['id']).values_list('uuid',flat=True)

        self.assertHttpCreated(resp)
        self.assertEqual(response_data['title'], dashboard_title)
        self.assertEqual(chart_uuids.split(','), [str(x) for x in db_chart_uuids])

    def test_dashboard_name_exist(self):
        dashboard_name = "test the already exists"

        CustomDashboard.objects.all().delete()
        self.assertEqual(CustomDashboard.objects.count(), 0)

        post_data = {'title': dashboard_name}
        resp = self.api_client.post('/api/v1/custom_dashboard/', format='json', \
                                    data=post_data, authentication=self.get_credentials())
        self.assertEqual(CustomDashboard.objects.count(), 1)

        resp = self.api_client.post('/api/v1/custom_dashboard/', format='json', \
                                    data=post_data, authentication=self.get_credentials())
        response_data = self.deserialize(resp)

        self.assertHttpApplicationError(resp)
        self.assertEqual(CustomDashboard.objects.count(), 1)
        self.assertEqual('the custom dashboard "{0}" already exists'.format(dashboard_name), response_data['error'])

    def test_dashboard_get_no_params(self):
        d1 = CustomDashboard.objects.create(title="1 d-board")
        d2 = CustomDashboard.objects.create(title="2 d-board")
        resp = self.api_client.get('/api/v1/custom_dashboard/',
                format='json', \
                authentication=self.get_credentials())

        self.assertHttpOK(resp)
        resp_data = self.deserialize(resp)
        self.assertEqual(len(resp_data['objects']), 2)

    def test_dashboard_get_rows(self):
        dboard_rows = json.dumps([{'charts':['fdfdf'], 'layout':1}, {'charts':['ddsds'], 'layout':2}])
        d1 = CustomDashboard.objects.create(title="1 d-board", rows=dboard_rows)
        resp = self.api_client.get('/api/v1/custom_dashboard/%s/' % d1.id,
                format='json', \
                authentication=self.get_credentials())

        self.assertValidJSONResponse(resp)
        response_data = self.deserialize(resp)
        self.assertEqual(response_data['rows'], dboard_rows)


    def test_dashboard_gets_charts(self):
        ## create a dashboard ##
        d = CustomDashboard.objects.create(title='Dashboard')

        ## create two charts ##
        c1 = CustomChart.objects.create(uuid = 'a',title = 'a',chart_json = '')
        c2 = CustomChart.objects.create(uuid = 'b',title = 'b',chart_json = '')

        ## relate the charts to the dashboard ##
        ctd1 = ChartToDashboard.objects.create(dashboard_id = d.id, \
            chart_id = c1.id)
        ctd2 = ChartToDashboard.objects.create(dashboard_id = d.id, \
            chart_id = c2.id)

        resp = self.api_client.get('/api/v1/custom_dashboard/%s/' % d.id,
                format='json', \
                authentication=self.get_credentials())

        self.assertValidJSONResponse(resp)
        response_data = self.deserialize(resp)
        self.assertEqual(len(response_data['charts']), 2)

    def test_delete_dashboard(self):

        CustomDashboard.objects.all().delete()

        ## create a dashboard ##
        d = CustomDashboard.objects.create(title='Dashboard')
        self.assertEqual(1, len(CustomDashboard.objects.all()))

        ## create two charts ##
        c1 = CustomChart.objects.create(uuid = 'a',title = 'a',chart_json = '')
        c2 = CustomChart.objects.create(uuid = 'b',title = 'b',chart_json = '')

        ## relate the charts to the dashboard ##
        ctd1 = ChartToDashboard.objects.create(dashboard_id = d.id, \
            chart_id = c1.id)
        ctd2 = ChartToDashboard.objects.create(dashboard_id = d.id, \
            chart_id = c2.id)    

        resp = self.api_client.delete('/api/v1/custom_dashboard/?id=%s' %d.id, format='json',
                                   authentication=self.get_credentials())

        self.assertHttpAccepted(resp)
        self.assertEqual(0, len(CustomDashboard.objects.all()))

    def test_delete_dashboard(self):
        dashboard_name = "test delete a dashboard"
    
        # Create the custom dashboard
        CustomDashboard.objects.all().delete()
        self.assertEqual(CustomDashboard.objects.count(), 0)
    
        dashboard = CustomDashboard.objects.create(title=dashboard_name, layout=1)
        self.assertEqual(CustomDashboard.objects.count(), 1)
    
        delete_url = '/api/v1/custom_dashboard/%s/' %str(dashboard.id) 
    
        resp = self.api_client.delete(delete_url, format='json', data={}, authentication=self.get_credentials())
    
        self.assertEqual(CustomDashboard.objects.count(), 0)





