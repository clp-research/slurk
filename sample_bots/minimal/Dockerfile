FROM python:3.7.2

RUN mkdir -p /usr/src/minimal
WORKDIR /usr/src/minimal

COPY sample_bots/minimal/requirements.txt /usr/src/minimal
RUN pip install --no-cache-dir -r requirements.txt

COPY sample_bots/minimal /usr/src/minimal

ENTRYPOINT ["python", "minimal.py"]
