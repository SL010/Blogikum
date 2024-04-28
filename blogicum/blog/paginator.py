from django.core.paginator import Paginator

from blog.constans import NUMBER_ELEMENTS


def paginator(request, post_list):
    paginator = Paginator(post_list, NUMBER_ELEMENTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
