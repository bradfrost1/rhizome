from tastypie.resources import ALL
from tastypie.bundle import Bundle
from tastypie import fields
from tastypie.resources import Resource
from pandas import DataFrame

from datapoints.models import *
from datapoints.api.meta_data import *



class ResultObject(object):
    '''
    This is the same as a row in the CSV export in which one row has a distinct
    region / campaign combination, and the remaing columns represent the
    indicators requested.  Indicators are a list of IndicatorObjects.
    '''

    campaign = None
    region = None
    # changed_by_id = None
    # indicators = []


class IndicatorObject(object):
    '''
    This object represents the indicators and values for the region/campaign
    combinations.  Within each Result Object, there are N Inidcator objects
    with the attributes listed below.
    '''
    indicator = None
    value = None
    is_agg = None
    datapoint_id = None



class DataPointResource(Resource):
    '''
    This Resource is custom and builds upon the tastypie Model Resource by
    overriding the methods coorsponding to GET requests.  For more information
    on creating custom api functionality see :
      https://gist.github.com/nomadjourney/794424
      http://django-tastypie.readthedocs.org/en/latest/non_orm_data_sources.html
    '''

    error = None
    campaign = fields.IntegerField(attribute = 'campaign')
    region = fields.IntegerField(attribute = 'region')



    class Meta(BaseApiResource.Meta):
        object_class = ResultObject
        resource_name = 'datapoint'
        max_limit = None
        # serializer = CustomSerializer()


    def get_object_list(self,request):

        results = []

        err,params = self.parse_url_params(request.GET)

        if err:
            self.error = err
            return results

        ## get distinct regions/campaigns for the provided indicators
        all_region_campaign_tuples = DataPoint.objects.filter(
            indicator__in=params['indicator__in'],\
            region__in=params['region__in']).values_list('region','campaign').distinct()

        ## throw error if the indicators yield no r/c couples
        if len(all_region_campaign_tuples) == 0:
            self.error = 'There are no datapoints for the parameters requested'
            return results

        the_offset, the_limit = int(params['the_offset']), int(params['the_limit'])

        ## build a dataframe with the region / campaign tuples and slice it
        ## in accordance to the_offset and the_limit
        df = DataFrame(list(all_region_campaign_tuples),columns=['region',\
            'campaign'])[the_offset:the_limit + the_offset]

        for row in df.values:

            print row
            new_obj = ResultObject()
            new_obj.region = row[0]
            new_obj.campaign = row[1]

            results.append(new_obj)

        return results


    def obj_get_list(self,bundle,**kwargs):
        '''
        Outer method for get_object_list... this calls get_object_list and
        could be a point at which additional filtering may be applied
        '''

        return self.get_object_list(bundle.request)

    def obj_get(self):
        # get one object from data source
        pk = int(kwargs['pk'])
        try:
            return data[pk]
        except KeyError:
            raise NotFound("Object not found")


    def alter_list_data_to_serialize(self, request, data):
        '''
        If there is an error for this resource, add that to the response.  If
        there is no error, than add this key, but set the value to null'''

        if self.error:
            data['error'] = self.error
        else:
            data['error'] = None

        return data


    ##########################
    ##### HELPER METHODS #####
    ##########################

    def parse_url_params(self,query_dict):

        parsed_params = {}

        optional_params = {
            'campaign__in':None,'campaign_end':None,\
            'campaign_start':None,'the_limit':10000,'the_offset':0,
            'uri_format':'id','agg_level':'mixed'}

        required_params = {'indicator__in': None,'region__in': None}

        for k,v in optional_params.iteritems():
            try:
                parsed_params[k] = query_dict[k]
            except KeyError:
                parsed_params[k] = v

        for k,v in required_params.iteritems():

            try:
                parsed_params[k] = query_dict[k].split(',')
            except KeyError as err:
                return str(err).replace('"','') + ' is a required paramater!', None

        return None, parsed_params
