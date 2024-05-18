# An extended Django REST Framework tutorial application

### Differences

- Query optimization

    For example `Snippet.objects.all().select_related('owner')`

- API throttling

    Authenticated users can do more requests per minute.
    Also not many snippets can be created in one minute.

- Tests
- Filtering. Ordering.
- JWT instead of sessions.
- OpenAPI (Swagger) instead of Browsable API.
- LimitOffsetPagination instead of PageNumberPagination.
- Manage snippets on the admin portal.
- Searching by ElasticSearch.

### Environment variables

- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DATABASE_NAME

- DJANGO_SECRET_KEY
- DJANGO_DEBUG
- ALLOWED_HOSTS

- ELASTICSEARCH_HOSTS (e.g. http://elasticsearch:9200)

### Initial setup

```bash
# Create ElasticSearch indicies.
python manage.py search_index --rebuild
```
