from rest_framework import mixins, viewsets


class RetriveAndListViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pass
