# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from rhizome.models import DataPoint, Campaign
from pandas import DataFrame
import math
import pandas as pd

# helper function for upsert_unique_indices


def add_unique_index(x):
    if x['campaign_id'] and not math.isnan(x['campaign_id']):
        x['unique_index'] = str(x['location_id']) + '_' + \
            str(x['indicator_id']) + '_' + str(int(x['campaign_id']))
    else:
        x['unique_index'] = str(x['location_id']) + '_' + str(x['indicator_id']) + \
            '_' + str(pd.to_datetime(x['data_date'], utc=True))
    return x


def upsert_unique_indices(apps, schema_editor):
    datapoint_values_list = [
        'id', 'created_at', 'indicator_id', 'location_id', 'campaign_id', 'data_date']
    historical_dps = DataFrame(list(DataPoint.objects.all()
                                    .values_list('id', 'created_at', 'indicator_id', 'location_id', 'campaign_id', 'data_date')), columns=datapoint_values_list)
    # create the unique index
    historical_dps = historical_dps.apply(add_unique_index, axis=1)

    # group by and max on created at, get the most recent upload
    historical_dps = historical_dps.sort("created_at", ascending=False).groupby(
        "unique_index", as_index=False).first()

    # get the ids into a list and select them
    dps_to_update = DataPoint.objects.filter(id__in=list(historical_dps['id']))
    print 'dps to update'
    print len(dps_to_update)
    # then run a query and update each
    for dp in dps_to_update:
        unique_index = historical_dps[historical_dps[
            'id'] == dp.id].iloc[0]['unique_index']
        dp.unique_index = unique_index
        dp.save()

    # delete all the other duplicates
    dps_to_delete = DataPoint.objects.all().exclude(
        id__in=list(historical_dps['id']))
    print 'dps_to_delete'
    print len(dps_to_delete)
    dps_to_delete.delete()

    dataframe_columns = ['id', 'created_at', 'indicator_id',
                         'location_id', 'campaign_id', 'data_date', 'unique_index']

    # make sure there aren't duplicate dps now.
    all_dps = DataFrame(list(DataPoint.objects.all()
                             .values_list('unique_index')), columns=['unique_index'])

    all_dps = all_dps.groupby('unique_index').size()

    for idx, dp in all_dps.iteritems():
        if dp != 1:
            raise Exception("there are duplicate datapoints")


class Migration(migrations.Migration):

    dependencies = [
        ('rhizome', '0014_unique_index_agg_refresh'),
    ]
    operations = [
        migrations.RunPython(upsert_unique_indices),

    ]