# Drftutorial

An extended Django REST Framework tutorial application.

### Differences

- Query optimization. Silk helps a lot.
- API throttling.
- Tests.
- Ordering by a DRF built-in filter.
- Filtering by Django-filter.
- Searching by ElasticSearch.
- JWT instead of sessions.
- OpenAPI (Swagger) instead of Browsable API.
- LimitOffsetPagination instead of PageNumberPagination.
- Gunicorn as a WSGI server.
- Manage snippets on the admin portal.
- Disable time zones.
- Introduce a new field: expired_at. So the app removes snippets which are expired.
  And it is implemented by using Celery and its periodic tasks feature.

### Initial setup

First of all, make sure you've created a .env file, put it in the root folder
and provided all required environment variables.

Then you have to create a PostgreSQL database.
Do not forget to use the same data that you provide in .env.
Also, you might want to create a new user to access the database from the app.
[Why do I have to do this?](https://stackoverflow.com/a/26373972)

```
CREATE DATABASE drftutorial WITH OWNER admin ENCODING 'utf-8';
```

Next, you want to apply migrations.

```bash
python manage.py migrate
```

If you are going to use the debug mode,
you have to apply migrations for the apps which are used only in this mode.

```bash
APP_DEBUG=True python manage.py migrate
```

Next, you want to set up ElasticSearch indexes.

```bash
# Create ElasticSearch indexes.
python manage.py search_index --rebuild
```

If you are going to run tests, you have to set up test indexes too.

```bash
python manage.py search_index --rebuild --settings drftutorial.settings_testing
```
