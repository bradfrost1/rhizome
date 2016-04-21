# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

import jsonfield.fields

from rhizome.etl_tasks.transform_upload import DateDocTransform
from rhizome.etl_tasks.refresh_master import MasterRefresh
from rhizome.models import *
import pandas as pd

def ingest_polio_cases(apps, schema_editor):

    indicator_id = Indicator.objects.create(
        name = 'Polio Cases',
        short_name = 'Polio Cases',
        description = 'Polio Cases',
        data_format = 'date_int'
    ).id

    som_id = SourceObjectMap.objects.create(
        content_type = 'indicator',
        master_object_id = indicator_id,
        source_object_code = 'polio_case'
    )

    document_id = process_source_sheet_df()

    polio_cases_count = DataPoint.objects.filter(
        indicator_id = indicator_id,
    ).count()

    doc_polio_cases_count = DocDataPoint.objects.filter(
        indicator_id = indicator_id,
    ).count()

    if polio_cases_count != 51:
        raise Exception('did not ingest the polio case data properly')


def process_source_sheet_df():

    user_id = 1
    sheet_name = 'AfgPolioCases.csv'
    # file_loc = settings.MEDIA_ROOT + sheet_name
    # saved_csv_file_location = settings.MEDIA_ROOT + sheet_name

    source_sheet_df = pd.read_csv(sheet_name)

    # doc_file_text = sheet_name + '.csv'

    new_doc = Document.objects.create(
        doc_title = sheet_name,
        guid = 'test'
    )

    # create_doc_details(new_doc.id)

    ## document -> source_submissions ##
    dt = DateDocTransform(user_id, new_doc.id, source_sheet_df)
    dt.process_file()

    ## source_submissions -> datapoints ##
    mr = MasterRefresh(user_id, new_doc.id)
    mr.main()

    return new_doc.id

class Migration(migrations.Migration):

    dependencies = [
        ('rhizome', '0012_datapoint_campaign_nullable'),
    ]

    operations = [
        migrations.RunPython(ingest_polio_cases)
    ]

# DROP TABLE IF EXISTS _polio_case_indicator;
# CREATE TABLE _polio_case_indicator AS
# SELECT ind.id FROM indicator ind WHERE name = 'Polio Cases';
#
# DELETE FROM source_object_map where content_type = 'indicator' AND master_object_id in (
#     SELECT id FROM _polio_case_indicator
# );
#
# DELETE FROM doc_datapoint WHERE indicator_id in (
#     SELECT id FROM _polio_case_indicator
# );
# DELETE FROM datapoint WHERE indicator_id in (
#     SELECT id FROM _polio_case_indicator
# );
# DELETE FROM indicator WHERE id in (
#     SELECT id FROM _polio_case_indicator
# );
# DELETE FROM source_submission where document_id in ( SELECT id FROM source_doc WHERE doc_title = 'AfgPolioCases.csv' );
# DELETE FROM source_doc WHERE doc_title = 'AfgPolioCases.csv';
# DELETE FROM django_migrations where name = '0013_ingest_polio_cases';