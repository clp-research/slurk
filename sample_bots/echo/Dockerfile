FROM python:3.7.2

RUN mkdir -p /usr/src/echo
WORKDIR /usr/src/echo

COPY sample_bots/echo/requirements.txt /usr/src/echo
RUN pip install --no-cache-dir -r requirements.txt

COPY sample_bots/echo /usr/src/echo

ENTRYPOINT ["python", "echo.py"]
