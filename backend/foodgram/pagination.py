"""Файл настройки паджинатора."""

from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPaginator(PageNumberPagination):
    """Класс настройки паджинатора."""

    page_size_query_param = 'limit'
