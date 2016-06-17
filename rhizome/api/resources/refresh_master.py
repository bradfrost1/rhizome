from rhizome.api.resources.base_non_model import BaseNonModelResource
from rhizome.models import DataPoint
from rhizome.models import Document
from rhizome.api.exceptions import RhizomeApiException
from rhizome.agg_tasks import AggRefresh

from rhizome.etl_tasks.refresh_master import MasterRefresh


class RefreshMasterResource(BaseNonModelResource):
    '''
    **GET Request** Runs refresh master, and agg refresh for a given document
        - *Required Parameters:*
            'document_id'
        - *Errors:*
            returns 500 error if no document id is provided
    '''
    class Meta(BaseNonModelResource.Meta):
        resource_name = 'refresh_master'
        GET_params_required = ['document_id']
        queryset = Document.objects.all().values()
        default_limit = 1

    def pre_process_data(self, request):
        '''
        Run the refresh master task for the document_id passed.

        Also, for any effected campaigns, run the aggrefersh on those in order
        to calculated aggregated and calcualted values.
        '''

        doc_id = request.GET.get('document_id', None)
        mr = MasterRefresh(request.user.id, doc_id)
        mr.main()

        doc_campaign_ids = set(list(DataPoint.objects
                        .filter(source_submission__document_id=doc_id)
                        .values_list('campaign_id', flat=True)))
        for c_id in doc_campaign_ids:
            AggRefresh(c_id)

        return Document.objects.filter(id=doc_id).values()
