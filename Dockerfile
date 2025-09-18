# download image of python3.13.7
FROM python:3.13.7-trixie
ENV PYTHONUNBUFFERED=1

WORKDIR /src

# install poetry
RUN pip install poetry

# copy dependency files
COPY pyproject.toml* poetry.lock* ./

# install libraries
RUN poetry config virtualenvs.in-project true
RUN if [ -f pyproject.toml ]; then poetry install --no-root; fi

# run server of uvicorn
ENTRYPOINT [ "poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--reload" ]