ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}

COPY init /
COPY queries /queries

# Install requirements
RUN pip install -r /requirements.txt

CMD /entrypoint.sh
