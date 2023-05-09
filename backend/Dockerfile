FROM python:3.10
LABEL author='stainy077@yandex.ru' version=2023.05

WORKDIR /app
COPY . /app
RUN python3 -m pip install --upgrade pip && \
    pip install -r /app/requirements.txt --no-cache-dir && \
    python3 /app/manage.py collectstatic --noinput
CMD python3 /app/manage.py migrate --noinput && \
    gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
