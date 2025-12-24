FROM nginx:alpine

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Копирование статических файлов
COPY . /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]