FROM python:3.7.2

RUN mkdir -p /usr/src/video
WORKDIR /usr/src/video

COPY sample_bots/video/requirements.txt /usr/src/video
RUN pip install --no-cache-dir -r requirements.txt

COPY sample_bots/video /usr/src/video

ENTRYPOINT ["python", "video.py"]
