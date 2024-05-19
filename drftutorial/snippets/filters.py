from django.utils.encoding import force_str

from rest_framework import filters
from rest_framework.settings import api_settings
from rest_framework.compat import coreapi, coreschema


class ElasticSeachFilter(filters.BaseFilterBackend):
    search_param = api_settings.SEARCH_PARAM
    search_title = 'Search'
    search_description = 'A search term.'

    def filter_queryset(self, request, queryset, view):
        get_elastic_search_query = getattr(view, 'get_elastic_search_query', None)
        search_term = request.query_params.get(self.search_param)
        if not (get_elastic_search_query and search_term):
            return queryset

        return get_elastic_search_query(search_term).filter_queryset(queryset)

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.search_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_str(self.search_title),
                    description=force_str(self.search_description)
                )
            )
        ]

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': self.search_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.search_description),
                'schema': {
                    'type': 'string',
                },
            },
        ]
