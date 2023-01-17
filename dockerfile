FROM python:3.10.4

WORKDIR app

COPY poetry.lock pyproject.toml ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
#RUN poetry cache clear --all .
RUN poetry install --no-dev

COPY . .
CMD ["poetry", "run", "python", "app.py"]

