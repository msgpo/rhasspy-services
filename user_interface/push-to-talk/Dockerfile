FROM alpine

RUN apk update
RUN apk add --no-cache nginx
RUN mkdir /run/nginx

COPY etc/nginx.conf /etc/nginx/conf.d/default.conf

ENTRYPOINT ["/usr/sbin/nginx", "-g", "daemon off;"]