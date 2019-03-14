FROM python:3.7.2

RUN mkdir -p /usr/src/slurk
WORKDIR /usr/src/slurk
COPY requirements.txt /usr/src/slurk
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/slurk
COPY docker/config.ini /usr/src/slurk
