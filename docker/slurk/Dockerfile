FROM python:3.7.2

RUN mkdir -p /usr/src/slurk
WORKDIR /usr/src/slurk
COPY . /usr/src/slurk
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["gunicorn", "-w", "1", "-b", ":5000", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "run:app"]
