FROM python:3.12

ARG USERNAME="peon"
ARG USER_UID=1000
ARG USER_GID=1000

ENV PYTHONUNBUFFERED 1

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

WORKDIR /app

RUN pip install poetry==1.8.2
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/
RUN poetry install --no-root --no-cache

COPY gunicorn.conf.py .

EXPOSE 8000

USER $USERNAME

CMD ["gunicorn"]
