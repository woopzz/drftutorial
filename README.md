# An extended Django REST Framework tutorial application

### Differences

- Query optimization

    For example `Snippet.objects.all().select_related('owner')`

- API throttling

    Authenticated users can do more requests per minute.
    Also not many snippets can be created in one minute.

- Tests

### Environment variables

- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DATABASE_NAME

- DJANGO_SECRET_KEY
- DJANGO_DEBUG
