import logging

from rest_framework.filters import OrderingFilter

logger = logging.getLogger(__name__)


class PersonOrdering(OrderingFilter):
    """自定义排序的主要目的是适应bootstrap-table的要求"""

    def filter_queryset(self, request, queryset, view):
        sort = request.query_params.get('sort')
        order = request.query_params.get('order')
        if sort:
            if order == 'asc':
                return queryset.order_by(sort)
            elif order == 'desc':
                return queryset.order_by('-{}'.format(sort))
            else:
                logger.warning('unsupported ordering type:{}'.format(order))
                return queryset
        elif order:
            if order == 'asc':
                return queryset.order_by('-is_active', 'id')
            elif order == 'desc':
                return queryset.order_by('-is_active', '-id')
            else:
                logger.warning('unsupported ordering type:{}'.format(order))
                return queryset
        else:
            return queryset


class RecordOrdering(OrderingFilter):
    """自定义排序的主要目的是适应bootstrap-table的要求"""

    def filter_queryset(self, request, queryset, view):
        sort = request.query_params.get('sort')
        order = request.query_params.get('order')
        if sort:
            if order == 'asc':
                return queryset.order_by(sort)
            elif order == 'desc':
                return queryset.order_by('-{}'.format(sort))
            else:
                logger.warning('unsupported ordering type:{}'.format(order))
                return queryset
        elif order:
            if order == 'asc':
                return queryset.order_by('-created')
            elif order == 'desc':
                return queryset.order_by('-created')
            else:
                logger.warning('unsupported ordering type:{}'.format(order))
                return queryset
        else:
            return queryset


