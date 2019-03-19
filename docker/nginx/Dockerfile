FROM nginx:1.15.8

RUN rm /etc/nginx/nginx.conf
COPY docker/nginx/nginx.conf /etc/nginx/

RUN rm /etc/nginx/conf.d/default.conf
COPY docker/nginx/project.conf /etc/nginx/conf.d/
