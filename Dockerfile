FROM python:3.7.8

RUN mkdir /app

COPY ./ /app
WORKDIR /app

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

RUN apt-get update
RUN apt-get install nano

RUN wget -q https://www.dropbox.com/s/nfb8o7d8e84j4le/python-task.zip?dl=1 --output-document algoseek.zip

RUN unzip algoseek.zip -d data

ENTRYPOINT ["/bin/bash"]