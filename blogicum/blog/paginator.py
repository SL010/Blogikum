from django.core.paginator import Paginator
from django.conf import settings


def paginator(request, post_list):
    paginator = Paginator(post_list, settings.NUMBER_ELEMENTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
