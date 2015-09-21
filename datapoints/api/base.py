import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import SessionAuthentication, ApiKeyAuthentication,\
    MultiAuthentication
from tastypie.resources import ModelResource, Resource, ALL
from tastypie.cache import SimpleCache

try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    def csrf_exempt(func):
        return func

from datapoints.models import LocationType, Location, LocationPermission, \
    LocationTree
from datapoints.api.serialize import CustomSerializer, CustomJSONSerializer

class CustomCache(SimpleCache):
    '''
    Set up to override the simple cache method in order to customize the
    behavior of the cache control headers.
    '''

    def cache_control(self):
        '''
        Instatiate the cache_control instance, and add the headers needed.
        '''
        control = super(CustomCache, self).cache_control()
        control.update({'must_revalidate':True, 'max_age': 3600})
        return control


class BaseModelResource(ModelResource):
    '''
    This applies to only the V1 API.  This method inherits from Tastypie's
    model resource.

    This resource strips down almost all of the tastypie functions which
    drastically slow down the API performance.

    IMPORTANT: if you note, all of the resources use the .values() option for
    each queryset.  That returns the model as JSON, so the idea is that the
    API does not need to serialize or dehydrate the resource.

    The models are set up so that the API does as little transformation as
    possible.  That means however, that a few of our metadata models ( see
    campaign / indicator ) are cached and contain related information making
    the job of the API easy.
    '''

    class Meta:
        authentication = MultiAuthentication(SessionAuthentication(),\
            ApiKeyAuthentication())
        authorization = DjangoAuthorization()
        always_return_data = True
        allowed_methods = ['get','post','put','patch', 'delete']
        # filtering = {
        # FIXME have subclass inherit this and add their own..
        #     "id": ALL,
        # }
        cache = CustomCache()
        serializer = CustomSerializer()

    def dispatch(self, request_type, request, **kwargs):
        """
        Overrides Tastypie and calls get_list.  For now, that makes these
        resources GET only. ( no POST / PUT / PATCH ).
        """

        # allowed_methods = getattr(self._meta, "%s_allowed_methods" % request_type, None)
        #
        # if 'HTTP_X_HTTP_METHOD_OVERRIDE' in request.META:
        #     request.method = request.META['HTTP_X_HTTP_METHOD_OVERRIDE']

        # request_method = self.method_check(request, allowed=allowed_methods)
        # method = getattr(self, "%s_%s" % (request_method, request_type), None)

        # if method is None:
        #     raise ImmediateHttpResponse(response=http.HttpNotImplemented())

        self.is_authenticated(request)
        self.throttle_check(request)
        # All clear. Process the request.

        # If what comes back isn't a ``HttpResponse``, assume that the
        # request was accepted and that some action occurred. This also
        # prevents Django from freaking out.

        # request = convert_post_to_put(request)
        # response = method(request, **kwargs)

        response = self.get_list(request, **kwargs)

        if not isinstance(response, HttpResponse):
            return http.HttpNoContent()

        return response

    def get_list(self, request, **kwargs):
        """
        Overriden from Tastypie..
        """

        base_bundle = self.build_bundle(request=request)
        objects = self.obj_get_list(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        bundles = []

        for obj in objects:
            if obj.has_key('submission_json'):
                # to do -> abstract this for all JSONField models
                obj['submission_json'] = json.loads(obj['submission_json'])

            bundles.append(obj)

        response_meta = {
            'limit':None, ## paginator.get_limit(),
            'offset': None, ## paginator.get_offset(),
            'total_count':len(objects),
        }

        response_data = {
            'objects': bundles,
            'meta': response_meta, ## add paginator info here..
            'error': None
        }

        return self.create_response(request, response_data)

class BaseNonModelResource(Resource):
    '''
    NOTE: This applies to only the V1 API.  This is only used for the
    /api/v1/datapoint endpoint.

    This is the top level class all other Resource Classes inherit from this.
    The API Key authentication is defined here and thus is required by all
    other resources.  This class enherits fro the Tastyppie "ModelResource"

    See Here: http://django-tastypie.readthedocs.org/en/latest/resources.html?highlight=modelresource
    '''

    class Meta():
        authentication = MultiAuthentication(SessionAuthentication(),\
            ApiKeyAuthentication())
        authorization = DjangoAuthorization()
        always_return_data = True
        cache = CustomCache()

    def parse_url_strings(self,query_dict):
        '''
        As the geo endpoint is based off of the location/parent_location paremeter
        we go through a pretty hacky try / except frenzy in order to find the
        parameters necessary to get location/shape data for the front end.  The
        parameters here for location_in,level, and parent_location in were
        constructed in accordance to the request from the front end team.
        '''

        self.location__in, self.location_type_id, self.parent_location__in = \
            None, None, None

        ## location_ID
        try:
            self.location__in = [int(r) for r in query_dict['location__in']\
                .split(',')]
        except KeyError:
            pass
        except ValueError:
            pass

        ## location TYPE ##
        try:
            self.rtype_id = LocationType.objects.get(name = query_dict\
                ['level'].lower()).id
        except KeyError:
            pass
        except ObjectDoesNotExist:
            all_r_types = LocationType.objects.all().values_list('name',flat=True)
            err = 'location type doesnt exist. options are:  %s' % all_r_types
            return err, []

        try:
            self.parent_location__in = [int(r) for r in query_dict['parent_location__in']\
                .split(',')]
        except KeyError:
            pass
        except ValueError:
            pass

        return None


    def get_locations_to_return_from_url(self,request):
        '''
        This method is used in both the /geo and /datapoint endpoints.  Based
        on the values parsed from the URL parameters find the locations needed
        to fulfill the request based on the four rules below.
        1  location__in returns geo data for the locations requested
        2. passing only parent_location__in  should return the shapes for all the
           immediate children in that location if no level parameter is supplied
        3. no params - return locations at the top of the tree ( no parent_id).
        After the four steps are worked through in this method, we apply the
        permissions function in order to determine the final list of locations
        to return based on the user making the request.
        '''

        ## attach these to self and return only error #
        err = self.parse_url_strings(request.GET)

        if err:
            self.err = err
            return err, []

        ## CASE 1 ##
        if self.location__in is not None:

            location_ids = Location.objects.filter(id__in = self.location__in)\
                .values_list('id',flat=True)

        ## CASE 2 #
        elif self.parent_location__in is not None and self.location_type_id is None:

            location_ids = Location.objects.filter(parent_location__in = \
                self.parent_location__in).values_list('id',flat=True)

        else:
            location_ids = Location.objects.filter(parent_location_id__isnull=True).\
                values_list('id',flat=True)

        return None, location_ids
