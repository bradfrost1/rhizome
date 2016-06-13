from base_test_case import RhizomeApiTestCase
from rhizome.models import Office, LocationType, Location, \
    LocationPermission, Campaign, CampaignType, IndicatorTag
from rhizome.cache_meta import LocationTreeCache
from setup_helpers import TestSetupHelpers


class CampaignResourceTest(RhizomeApiTestCase):

    def setUp(self):

        ## instantiate the test client and all other methods ##
        super(CampaignResourceTest, self).setUp()

        self.ts = TestSetupHelpers()
        self.lt = self.ts.create_arbitrary_location_type()
        self.o = self.ts.create_arbitrary_office()
        self.not_allowed_to_see_location = self.ts.create_arbitrary_location(
            self.lt.id,
            self.o.id)

        self.top_lvl_location = self.ts.create_arbitrary_location(
            self.lt.id,
            self.o.id,
            location_code='Nigeria',
            location_name='Nigeria')

        self.sub_location = self.ts.create_arbitrary_location(
            self.lt.id,
            self.o.id,
            location_name='Kano',
            location_code='Kano',
            parent_location_id=self.top_lvl_location.id)

        self.it = IndicatorTag.objects.create(tag_name='Polio')

        self.ct = CampaignType.objects.create(name='NID')
        self.can_see_campaign = self.ts.create_arbitrary_campaign(
            office_id=self.ts.create_arbitrary_office(name='test1').id,
            campaign_type_id=self.ct.id,
            location_id=self.top_lvl_location.id,
            indicator_tag_id=self.it.id,
            name="can_see"
        )

        self.can_see_campaign_2 = self.ts.create_arbitrary_campaign(
            office_id=self.ts.create_arbitrary_office(name='test2').id,
            campaign_type_id=self.ct.id,
            location_id=self.top_lvl_location.id,
            indicator_tag_id=self.it.id,
            name="can_see2"
        )

        self.can_not_see_campaign = self.ts.create_arbitrary_campaign(
            office_id=self.o.id,
            campaign_type_id=self.ct.id,
            location_id=self.not_allowed_to_see_location.id,
            indicator_tag_id=self.it.id,
        )

        ### set the user permission ###
        LocationPermission.objects.create(user_id=self.ts.user.id,
                                          top_lvl_location_id=self.top_lvl_location.id)

        self.ts.get_credentials(self)

        ltr = LocationTreeCache()
        ltr.main()

    def test_campaign_get(self):

        resp = self.ts.get(self, '/api/v1/campaign/')
        self.assertHttpOK(resp)
        response_data = self.deserialize(resp)
        self.assertEqual(len(response_data['objects']), 2)

    def test_campaign_get_id_list(self):
        campaign_id_list = [self.can_see_campaign.id,
                            self.can_see_campaign_2.id]
        data = {'id__in': str(campaign_id_list).strip('[]')}
        resp = self.ts.get(self, '/api/v1/campaign/', data=data)
        response_data = self.deserialize(resp)
        self.assertHttpOK(resp)
        self.assertEqual(len(response_data['objects']), 2)

    def test_campaign_get_id_list_invalid(self):
        data = {'id__in': 12345}
        resp = self.ts.get(self, '/api/v1/campaign/', data=data)
        response_data = self.deserialize(resp)
        self.assertHttpOK(resp)
        self.assertEqual(len(response_data['objects']), 0)

    def test_get_detail(self):
        detailURL = '/api/v1/campaign/{0}/'.format(self.can_see_campaign.id)
        resp = self.ts.get(self, detailURL)
        self.assertHttpOK(resp)
        response_data = self.deserialize(resp)
        self.assertEqual(self.can_see_campaign.name, response_data['name'])

    def test_get_detail_invalid_id(self):
        detailURL = '/api/v1/campaign/12345/'
        resp = self.ts.get(self, detailURL)
        self.assertHttpApplicationError(resp)

    def test_post_campaign(self):
        data = {
            'name': 'something',
            'top_lvl_location_id': self.top_lvl_location.id,
            'top_lvl_indicator_tag_id': self.it.id,
            'office_id': self.o.id,
            'campaign_type_id': self.ct.id,
            'start_date': '2016-05-01',
            'end_date': '2016-05-01',
            'pct_complete': 0.1
        }
        resp = self.ts.post(self, '/api/v1/campaign/', data=data)
        response_data = self.deserialize(resp)
        self.assertHttpCreated(resp)
        self.assertEqual(response_data['name'], 'something')

    def test_post_campaign_with_id(self):
        id_val = 1345
        data = {
            'name': 'something',
            'top_lvl_location_id': self.top_lvl_location.id,
            'top_lvl_indicator_tag_id': self.it.id,
            'office_id': self.o.id,
            'campaign_type_id': self.ct.id,
            'start_date': '2016-05-01',
            'end_date': '2016-05-01',
            'pct_complete': 0.1,
            'id': id_val
        }
        resp = self.ts.post(self, '/api/v1/campaign/', data=data)
        response_data = self.deserialize(resp)
        self.assertHttpCreated(resp)
        self.assertEqual(response_data['id'], id_val)

    def test_post_campaign_missing_field(self):
        data = {
            'top_lvl_indicator_tag_id': self.it.id,
            'office_id': self.o.id,
            'campaign_type_id': self.ct.id,
            'start_date': '2016-05-01',
            'end_date': '2016-05-01',
            'pct_complete': 0.1
        }
        resp = self.ts.post(self, '/api/v1/campaign/', data=data)
        self.assertHttpApplicationError(resp)

    def test_post_campaign_invalid_ids(self):
        data = {
            'name': 'something',
            'top_lvl_location_id': 0,
            'top_lvl_indicator_tag_id': 33,
            'office_id': self.o.id,
            'campaign_type_id': self.ct.id,
            'start_date': '2016-05-01',
            'end_date': '2016-05-01',
            'pct_complete': 0.1
        }
        resp = self.ts.post(self, '/api/v1/campaign/', data=data)
        self.assertHttpApplicationError(resp)
