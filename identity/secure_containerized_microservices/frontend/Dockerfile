FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY ./html/. /var/www/html/
COPY my-site.conf /etc/nginx/conf.d/my-site.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
