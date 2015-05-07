import json
import datetime

from django.core.serializers import json as djangojson
from django.db.models import Model
from django.db.models.query import RawQuerySet
from django.db.models.sql.constants import QUERY_TERMS
from django.forms.models import model_to_dict
from django.utils.encoding import smart_str
from django.contrib.auth.models import User, Group
from django.core import serializers

from datapoints.models import *



class v2Request(object):

    def __init__(self,request, content_type):

        self.request = request
        self.content_type = content_type
        self.user_id = request.user.id

        self.db_obj = self.object_lookup(content_type)
        self.db_columns = self.db_obj._meta.get_all_field_names()

        self.kwargs = self.clean_kwargs(request.GET)  ## CHANGE TO POST ##


    def clean_kwargs(self,query_dict):
        '''
        When passing filters make sure that what is in the URL string is
        actually a field of the model.
        '''

        cleaned_kwargs = {}
        operator_lookup = {}

        for param in query_dict.keys():

            try:
                operator_lookup[param[0:param.index('__')]] = param
            except ValueError:
                operator_lookup[param] = param


        keys = list(set(self.db_columns).intersection(k for k in operator_lookup.keys()))

        for k in keys:

            query_key = operator_lookup[k]
            query_value = query_dict[operator_lookup[k]]#[]

            if "," in query_value:
                cleaned_kwargs[query_key] = query_value.split(',')
            else:
                cleaned_kwargs[query_key] = query_value

        print 'CLEANED KWARGS'#cleaned_kwargs
        print cleaned_kwargs

        return cleaned_kwargs


    def object_lookup(self,content_type_string):

        ## I CAN CHANGE THIS TO ADD THE FUNCTION IT NEEDS FOR PERMISSIONS ##
        orm_mapping = {
            # 'datapoint': DataPointAbstracted,
            'indicator': Indicator,
            'campaign': Campaign,
            'region': Region,
            'group': Group,
            'user': User,
        }

        db_model = orm_mapping[content_type_string]

        return db_model


class v2PostRequest(v2Request):


    def main(self):
        '''
        Create an object in accordance to the URL kwargs and return the new ID
        '''

        new_obj = self.db_obj.objects.create(**self.kwargs)

        data = {'new_id':new_obj.id }

        return None, data



class v2GetRequest(v2Request):


    def main(self):
        '''
        Get the list of database objects ( ids ) by applying the URL kwargs to
        the filter method of the djanog ORM.
        '''

        # if not self.kwargs and self.content_type == 'Region':
        #     ## WHEN ASKING FOR ALL REGIONS, DONT HIT REGION TABLE TWICE ##
        #     qset = None
        #
        # else:
        #     print 'I AM HERE'
        #     qset = list(self.db_obj.objects.all().filter(**self.kwargs)\

        qset = list(self.db_obj.objects.all().filter(**self.kwargs).values())
        filtered_data = self.apply_permissions(qset)
        data = self.serialize(filtered_data)

        return None, data

    def apply_permissions(self, queryset):
        '''
        Right now this is only for regions and Datapoints.

        Returns a Raw Queryset
        '''

        if self.content_type == 'region':

            list_of_object_ids = [x['id'] for x in queryset]

            data = Region.objects.raw("SELECT * FROM\
                fn_get_authorized_regions_by_user(%s,%s)",[self.request.user.id,\
                list_of_object_ids])

            return data

        elif self.content_type == 'campaign':

            list_of_object_ids = [x['id'] for x in queryset]

            data = Campaign.objects.raw("""
                SELECT c.* FROM campaign c
                INNER JOIN datapoint_abstracted da
                    ON c.id = da.campaign_id
                INNER JOIN region_permission rm
                    ON da.region_id = rm.region_id
                    AND rm.user_id = %s
                WHERE c.id = ANY(%s)""",[self.user_id, list_of_object_ids])

            return data

        else:
             return queryset



    def serialize(self, data):

        serialized = [self.clean_row_result(row) for row in data]

        return serialized

    def clean_row_result(self, row_data):
        '''
        When Serializing, everything but Int is converted to string.

        If it is a raw queryset, first convert the row to a dict using the
        built in __dict__ method.

        This just returns a list of dict.  The JsonResponse in the view
        does the actual json conversion.
        '''

        cleaned_row_data = {}

        if isinstance(row_data,Model): # if raw queryset, convert to dict
            row_data = dict(row_data.__dict__)

        for k,v in row_data.iteritems():
            if isinstance(v, int):
                cleaned_row_data[k] = v
            else:
                cleaned_row_data[k] = smart_str(v)

        return cleaned_row_data
