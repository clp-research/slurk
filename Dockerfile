FROM python:3.9

RUN mkdir -p /usr/src/slurk
WORKDIR /usr/src/slurk

COPY requirements.txt /usr/src/slurk
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn gevent-websocket

COPY app /usr/src/slurk/app

EXPOSE 5000
ENTRYPOINT ["gunicorn", "-b", ":5000", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "slurk:create_app()"]
