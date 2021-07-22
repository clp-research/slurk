FROM python:3.9

RUN mkdir -p /usr/src/slurk
WORKDIR /usr/src

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt
run rm /tmp/requirements.txt

COPY slurk /usr/src/slurk

EXPOSE 80
ENTRYPOINT ["gunicorn", "-b", ":80", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "slurk:create_app()"]
