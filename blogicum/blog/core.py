from django.core.paginator import Paginator
from django.db.models import Count
from django.utils.timezone import now

from blog.models import Post
from blogicum.settings import NUMBER_ELEMENTS


def paginator(request, post_list):
    paginator = Paginator(post_list, NUMBER_ELEMENTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_post(post=Post.objects, query_1=False, query_2=False):
    posts = post.select_related('category', 'author', 'location')
    if query_1:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=now()
        )
    if query_2:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=now()).annotate(
                comment_count=Count('comments')
        ).order_by('-pub_date')
    return posts
