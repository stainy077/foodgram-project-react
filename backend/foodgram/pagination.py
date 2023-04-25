from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPaginator(PageNumberPagination):
    """Настройка паджинатора."""

    page_size_query_param = 'limit'
