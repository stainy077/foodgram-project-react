FROM python:3.7-slim
LABEL author='stainy077@yandex.ru' version=2023.05

WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip && \
    pip install -r /app/requirements.txt --no-cache-dir && \
    python /app/manage.py collectstatic --noinput
CMD python /app/manage.py migrate --noinput && \
    gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
