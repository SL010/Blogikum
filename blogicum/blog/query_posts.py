from django.db.models import Count
from django.utils.timezone import now

from blog.models import Post


def get_posts(manager=Post.objects, filtration=False, annotation=False):
    posts = manager.select_related('category', 'author', 'location')
    if filtration:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=now()
        )
    if annotation:
        posts = posts.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    return posts
