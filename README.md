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

### Dev setup

1. Create a database user and a database itself.

[Why do I have to do this?](https://stackoverflow.com/a/26373972)

```
CREATE USER drftutorial WITH PASSWORD 'drftutorial';
CREATE DATABASE drftutorial WITH OWNER drftutorial ENCODING 'utf-8';
```

2. Appy migrations.

```bash
python manage.py migrate
```

If you are going to use the debug mode,
you have to apply migrations for the apps which are used only in this mode.

```bash
APP_DEBUG=True python manage.py migrate
```

3. Create ElasticSearch indexes.

```bash
# Create ElasticSearch indexes.
python manage.py search_index --rebuild
```

If you are going to run tests, you have to set up test indexes too.

```bash
python manage.py search_index --rebuild --settings drftutorial.settings_testing
```

### Deploy (AWS)

We need the following AWS resources:
1. An RDS instance for PostgreSQL.
2. Two EC2 instances. One for ElasticSearch, two for other services (the app itself, the celery worker and the celer beat worker).

I consider only free tier, so t2.micro is the only available choice for EC2.
I'd like ElasticSearch to be together with other services together, but it takes up too much RAM, so one t2.micro instance crashes.

#### Terraform

Terraform is an infrastructure as code tool. So we don't need to run EC2 instances, an RDS instance, create security groups and so on by hand.
What we do need is to type `terraform apply`.

There is a cool video about Terraform basics on Youtube: [Why You NEED To Learn Terraform | Practical Tutorial](https://youtu.be/nvNqfgojocs)

The configuration expects a public key named `drftutorial.pub` to be in the same folder with tf files. Quick note how to create an RSA key:

```bash
ssh-keygen -b 2048 -t rsa
```

#### EC2 (ElasticSearch)

In my experience, "Amazon linux 2023 AMI" works much better than "Amazon linux 2 AMI".
But it doesn't have "amazon-linux-extras". Long story short, we can find out how to install docker [here (Installing Docker on AL2023)](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-container-image.html).

1. Install docker.
2. Run an elasticsearch container with the following command:

```bash
docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "ES_JAVA_OPTS=-Xms128m -Xmx128m" elasticsearch:8.13.4
```

#### EC2 (Main)

1. Install docker.
2. Install docker-compose.

There is no official guide on AWS pages. Most relevant answers in Google suggests to download a relase version from Github.

```bash
sudo curl -L https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. Copy `docker-compose.yml` from the root folder.

```
scp -i terraform/drftutorial docker-compose.yml ec2-user@ec2_main_public_ip:/home/ec2-user
```

4. Create a file `.env` near `docker-compose.yml` and fill it in.

We can use `.devcontainer/.env` as an example. We can even copy this file to the instance and edit it.

5. Create a new database.

Only the main EC2 instance have access to the RDS instance. It means we can create a database only from this instance itself.
We need `psql` and the easiest way to get it is to use a postgres docker container.

```bash
docker run -it --rm postgres:16.2 psql "host=RDS_HOST port=RDS_PORT dbname=postgres user=RDS_USER password=RDS_PASSWORD"
```

```sql
CREATE DATABASE drftutorial WITH OWNER RDS_USER ENCODING 'utf-8';
```

6. Check connection with the Elasticsearch EC2 instance.

```
curl "http://ES_HOST:ES_PORT/"
```

7. Run migrations and build ES indexes.

```bash
docker-compose run app python3 manage.py migrate
docker-compose run app python3 manage.py search_index --rebuild
```

8. Run containers.

```bash
docker-compose up -d
```
