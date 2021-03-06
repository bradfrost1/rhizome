from django.test import TestCase
from django.contrib.auth.models import User
from pandas import read_csv, notnull, to_datetime

from rhizome.models.campaign_models import Campaign, CampaignType, \
    DataPointComputed
from rhizome.models.location_models import Location
from rhizome.models.indicator_models import Indicator, IndicatorTag
from rhizome.models.document_models import Document, \
    DocumentSourceObjectMap, SourceObjectMap

from rhizome.cache_meta import LocationTreeCache

class TransformUploadTestCase(TestCase):

    def __init__(self, *args, **kwargs):

        super(TransformUploadTestCase, self).__init__(*args, **kwargs)

    def setUp(self):

        self.create_metadata()
        self.user = User.objects.get(username='test')
        self.location_list = Location.objects.all().values_list('name', flat=True)

    def test_simple_campaign_upload(self):

        doc_id = self.ingest_file('eoc_post_campaign.csv')
        doc_obj = Document.objects.get(id = doc_id)
        doc_obj.transform_upload()
        doc_obj.refresh_master()

        # now take the datapoints to the computed datapoint table #
        campaign_object = Campaign.objects.get(id = self.mapped_campaign_id)
        campaign_object.aggregate_and_calculate()

        the_value_from_the_database = DataPointComputed.objects.get(
            campaign_id=self.mapped_campaign_id,
            indicator_id=self.mapped_indicator_with_data,
            location_id=self.mapped_location_id
        ).value

        some_cell_value_from_the_file = 0.082670906
        # find this from the data frame by selecting the cell where we have
        # mapped the data..

        self.assertEqual(some_cell_value_from_the_file,
                         the_value_from_the_database)

    def test_upload_new_data(self):

        file_and_cell_vals = {
            'eoc_post_campaign.csv': 0.082670906, 'modified_single_cell.csv': 0.0324}

        for f, cell_val_from_file in file_and_cell_vals.iteritems():
            doc_id = self.ingest_file(f)
            document_object = Document.objects.get(id = doc_id)
            document_object.transform_upload()
            document_object.refresh_master()

            campaign_object = Campaign.objects.get(id = self.mapped_campaign_id)
            campaign_object.aggregate_and_calculate()

            the_value_from_the_database = DataPointComputed.objects.get(
                campaign_id=self.mapped_campaign_id,
                indicator_id=self.mapped_indicator_with_data,
                location_id=self.mapped_location_id
            ).value

            # test that the file cell value reflects that in the database
            self.assertEqual(cell_val_from_file, the_value_from_the_database)

    def test_upsert_source_object_map(self):
        source_map_entry = SourceObjectMap.objects.filter(
            source_object_code='AF001039006000000000',
            content_type='location'
        )
        self.assertEqual(0, len(source_map_entry))

        document_id = self.ingest_file('eoc_post_campaign.csv')

        source_map_entry = SourceObjectMap.objects.filter(
            source_object_code='AF001039006000000000',
            content_type='location'
        )
        self.assertEqual(1, len(source_map_entry))

        # makes sure that we update DSOM as well
        dsom_entry = DocumentSourceObjectMap.objects.filter(
            document_id=document_id,
            source_object_map_id=source_map_entry[0].id)
        self.assertEqual(1, len(dsom_entry))

    def test_dupe_metadata_mapping(self):

        # duplicate of master_object_id that's used in create_metadata
        indicator_map = SourceObjectMap.objects.create(
            source_object_code='Percent missed due to not visited',
            content_type='indicator',
            mapped_by_id=self.user_id,
            master_object_id=self.mapped_indicator_with_data
        )

        self.ingest_file('eoc_post_campaign.csv')

        # the indicator should have not been added
        try:
            the_value_from_the_database = DataPointComputed.objects.get(
                campaign_id=self.mapped_campaign_id,
                indicator_id=self.mapped_indicator_with_data,
                location_id=self.mapped_location_id
            )
            fail("the value should not have been added due to duplicated indicator id")
        except DataPointComputed.DoesNotExist:
            pass

    def create_metadata(self):
        '''
        Creating the Indicator, location, Campaign, meta data needed for the
        system to aggregate / caclulate.
        '''

        top_lvl_tag = IndicatorTag.objects.create(id=1, tag_name='Polio')

        campaign_df = read_csv('rhizome/tests/_data/campaigns.csv')
        campaign_df['start_date'] = to_datetime(campaign_df['start_date'])
        campaign_df['end_date'] = to_datetime(campaign_df['end_date'])

        location_df = read_csv('rhizome/tests/_data/locations.csv')
        indicator_df = read_csv('rhizome/tests/_data/indicators.csv')

        campaign_type = CampaignType.objects.create(id=1, name="test")

        locations = self.model_df_to_data(location_df, Location)
        campaigns = self.model_df_to_data(campaign_df, Campaign)
        indicators = self.model_df_to_data(indicator_df, Indicator)

        self.user_id = User.objects.create_user(
            'test', 'test@test.com', 'test').id
        self.mapped_location_id = locations[0].id

        loc_map = SourceObjectMap.objects.create(
            source_object_code='AF001039003000000000',
            content_type='location',
            mapped_by_id=self.user_id,
            master_object_id=self.mapped_location_id
        )

        source_campaign_string = '2016 March NID OPV'
        self.mapped_campaign_id = campaigns[0].id
        campaign_map = SourceObjectMap.objects.create(
            source_object_code=source_campaign_string,
            content_type='campaign',
            mapped_by_id=self.user_id,
            master_object_id=self.mapped_campaign_id
        )
        self.mapped_indicator_id_0 = indicators[0].id
        indicator_map = SourceObjectMap.objects.create(
            source_object_code='Percent missed children_PCA',
            content_type='indicator',
            mapped_by_id=self.user_id,
            master_object_id=self.mapped_indicator_id_0
        )

        self.mapped_indicator_with_data = locations[2].id
        indicator_map = SourceObjectMap.objects.create(
            source_object_code='Percent missed due to other reasons',
            content_type='indicator',
            mapped_by_id=self.user_id,
            master_object_id=self.mapped_indicator_with_data
        )
        ## make sure that the location tree is updated ##

        ltc = LocationTreeCache()
        ltc.main()

    def model_df_to_data(self, model_df, model):

        meta_ids = []

        non_null_df = model_df.where((notnull(model_df)), None)
        list_of_dicts = non_null_df.transpose().to_dict()

        for row_ix, row_dict in list_of_dicts.iteritems():

            row_id = model.objects.create(**row_dict)
            meta_ids.append(row_id)

        return meta_ids

    def ingest_file(self, file_name):
        ## create one doc ##
        document = Document.objects.create(
            doc_title=file_name,
            created_by_id=self.user_id,
            guid='test')
        document.docfile = file_name
        document.save()

        document.transform_upload()
        document.refresh_master()

        return document.id
