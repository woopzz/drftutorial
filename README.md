# Drftutorial

An extended Django REST Framework tutorial application.

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
- Disable time zones.
- Introduce a new field: expired_at. So the app removes snippets which are expired.
  And it is implemented by using Celery and its periodic tasks feature.
- Gunicorn.

### Environment variables

- POSTGRES_HOST (e.g. db)
- POSTGRES_PORT (e.g. 5432)
- POSTGRES_USER (e.g. admin)
- POSTGRES_PASSWORD (e.g. admin)
- POSTGRES_DATABASE_NAME (e.g. drftutorial)

- DJANGO_SECRET_KEY (e.g. secret)
- DJANGO_DEBUG (e.g. False)
- ALLOWED_HOSTS (e.g. ['0.0.0.0'])

- ELASTICSEARCH_HOSTS (e.g. http://elasticsearch:9200)

- CELERY_BROKER_URL (e.g. redis://redis:6379/0)

### Initial setup

```bash
# Create ElasticSearch indicies.
python manage.py search_index --rebuild
```
