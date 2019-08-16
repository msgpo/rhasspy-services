FROM alpine

RUN apk update && \
    apk add --no-cache nginx

RUN mkdir -p /run/nginx

UI_DIR=user_interface/push-to-talk

COPY docker/${UI_DIR}/nginx.conf /etc/nginx/conf.d/default.conf

COPY ${UI_DIR}/ /www/

ENTRYPOINT ["/usr/sbin/nginx", "-g", "daemon off;"]