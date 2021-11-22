ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}

COPY init /

# Install requirements
RUN apt-get update && apt-get install netcat -y
RUN pip install -r /requirements.txt

CMD /entrypoint.sh
