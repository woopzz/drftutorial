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
CREATE USER django WITH PASSWORD 'django';
CREATE DATABASE drftutorial WITH OWNER django ENCODING 'utf-8';
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

### Deploy (AWS)

I consider only free tier, so t2.micro (1Gb RAM) is the only option I have.
I launched an RDS instance for a database, so I do not need it in `docker-compose.yml`.

I changed ES_JAVA_OPTS to allocate only 128Mb of RAM to the JVM heap.
`docker stats` shows me that the ElasticSearch container eats about 550Mb in this configuration.
I tried to decrease the value to 68Mb, but it's not enough for ES. It crashed soon after it started. So, 128Mb.

I tried to run my docker-compose.yml (except PostgreSQL).
And it went out of RAM pretty quick. So I decided to run ElasticSearch on a different instance.

So, we have two t2.micron instances. One for ElasticSearch and another one for the app, the celery worker and the celery beat worker.
We want to install docker on both of them. In my experience, "Amazon linux 2023 AMI" works much better than "Amazon linux 2 AMI".
But it doesn't have "amazon-linux-extras". Long story short, we can find instructions [here (Installing Docker on AL2023)](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-container-image.html).

#### EC2 (ElasticSearch)

Start an ElasticSearch container with this command:

```bash
docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "ES_JAVA_OPTS=-Xms128m -Xmx128m" elasticsearch:8.13.4
```

#### EC2 (Main)

Prepare the database.

I keep the RDS instance in a private subnet, so I can access it only from inside of its VPC.
I decided to use psql from the official PostgreSQL docker image.

```bash
docker run -it --rm postgres:16.2 psql "host=RDS_HOST port=RDS_PORT user=MASTER_USER password=MASTER_PASSWORD"
```

Create a new user and a database via psql. Put the user info into the environment file.

Run migrations and build ES indexes.

```bash
docker-compose run app python3 manage.py migrate
docker-compose run app python3 manage.py search_index --rebuild
```

By the way, here is a simple way to check indexes:

```
curl "http://ES_HOST:ES_PORT/snippet/_search?pretty=true&q=*:*"
```
