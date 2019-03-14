FROM python:3.7

RUN set -eux; \
    apt-get update; \
    apt-get install --no-install-recommends --no-install-suggests -y \
    nginx \
    ;

# COPY . /usr/src/slurk

# RUN pip3 install -r /usr/src/slurk/requirements.txt

RUN useradd --no-create-home nginx
RUN rm /etc/nginx/sites-enabled/default

COPY docker/slurk.conf /etc/nginx/conf.d/


# RUN cd /usr/src; \
# wget --no-check-certificate https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tgz; \
# tar xzf Python-3.7.2.tgz; \
# cd Python-3.7.2; \
# ./configure --enable-optimizations; \
# make -j4

# RUN make install;

# COPY . /usr/src/slurk

WORKDIR /usr/src/slurk

RUN chmod a+r /usr/src/slurk;
