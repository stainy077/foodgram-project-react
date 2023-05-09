# Foodgram

## Описание
Сервис позволяет авторизованным пользователям публиковать рецепты, подписываться на публикации других авторизованных пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
Неавторизованным пользователям доступна регистрация, авторизация, просмотр рецептов других авторов.

## Технологии
- Python
- Django
- Django REST Framework
- PostgreSQL
- Nginx
- gunicorn
- Docker
- GitHub
- Yandex.Cloud

## Шаблон наполнения env-файла:
SECRET_KEY=<>
DEBUG=<>
AL_HOSTS=<>
DB_ENGINE=<>
DB_NAME=<>
DB_USER=<>
DB_PASSWORD=<>
DB_HOST=<>
DB_PORT=<>

### Запуск сборки контейнеров docker-compose:
docker-compose up -d --build
### Проведение миграций внутри web-контейнера:
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
### Создание суперпользователя:
docker-compose exec backend python manage.py createsuperuser
### Сбор статики:
docker-compose exec backend python manage.py collectstatic --no-input
### Установка тестовой базы данных внутри web-контейнера:
docker-compose exec backend python manage.py loaddata fixtures.json


##### Проект доступен по адресу:
http://158.160.19.188/

##### Аккаунт администратора Django:
- Пользователь: admin@user.ru
- Пароль: admin

### Автор
Столярова Юлия















