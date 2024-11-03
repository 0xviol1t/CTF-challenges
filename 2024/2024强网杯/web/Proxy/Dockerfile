FROM nginx:1.27.0-alpine@sha256:208b70eefac13ee9be00e486f79c695b15cef861c680527171a27d253d834be9

COPY conf/ /etc/nginx/conf.d/
COPY proxy /app/proxy
COPY readflag /readflag
COPY entrypoint.sh /entrypoint.sh

RUN adduser --disabled-password --no-create-home --gecos "" --shell /bin/sh app &&\
    chmod 700 /entrypoint.sh &&\
    chown -R app:app /app &&\
    chmod -R 700 /app &&\
    chmod 4755 /readflag

CMD ["/entrypoint.sh"]