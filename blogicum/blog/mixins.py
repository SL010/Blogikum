from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, reverse

from blog.models import Comment


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class ChangeCommentMixin(OnlyAuthorMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_object(self):
        post = get_object_or_404(
            Comment,
            pk=self.kwargs[self.pk_url_kwarg],
            post__id=self.kwargs['post_id']
        )
        return post

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
