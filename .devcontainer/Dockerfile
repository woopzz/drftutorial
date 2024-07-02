FROM python:3.12

ARG USERNAME="peon"
ARG USER_UID=1000
ARG USER_GID=1000

ARG WORKDIR=/app

ENV PYTHONUNBUFFERED 1

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

WORKDIR $WORKDIR

RUN pip install poetry==1.8.2
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml $WORKDIR
RUN poetry install --no-root --no-cache

COPY drftutorial/ $WORKDIR/drftutorial
COPY manage.py $WORKDIR
COPY gunicorn.conf.py $WORKDIR

RUN chown -R $USERNAME:$USERNAME $WORKDIR

EXPOSE 8000

USER $USERNAME

CMD ["gunicorn"]
