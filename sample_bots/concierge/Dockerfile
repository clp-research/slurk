FROM python:3.7.2

RUN mkdir -p /usr/src/concierge
WORKDIR /usr/src/concierge

COPY sample_bots/concierge/requirements.txt /usr/src/concierge
RUN pip install --no-cache-dir -r requirements.txt

COPY sample_bots/concierge /usr/src/concierge

ENTRYPOINT ["python", "concierge.py"]
