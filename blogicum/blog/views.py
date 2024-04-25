from django.db.models import Count
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpRequest, Http404
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.utils.timezone import now
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from blog.models import Post, Category, Comment
from blog.forms import PostForm, CommentForm

User = get_user_model()


def get_queryset():
    return (
        Post.objects.select_related(
            'category', 'author', 'location'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=now()
        )
    )


def index(request: HttpRequest) -> HttpResponse:
    """Функция отображает посты на главной странице"""
    post_list = get_queryset().annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = (
        {'page_obj': page_obj}
    )
    return render(request, 'blog/index.html', context)


def category_posts(request: HttpRequest, category_slug: str) -> HttpResponse:
    """Функция отображает посты из выбранной категории"""
    category = get_object_or_404(
        Category.objects.filter(
            slug=category_slug,
            is_published=True
        )
    )
    post_list = get_queryset().filter(
        category__slug=category_slug).annotate(
            comment_count=Count('comments')
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostDetailView(DetailView):
    """CBV для отображения публикации"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.get_object().comments.prefetch_related('author').all()
        )
        return context

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if (post.is_published == 0
                or post.category.is_published == 0
                or post.pub_date > now()):
            if post.author != self.request.user:
                raise Http404
        return super().dispatch(request, *args, **kwargs)


def profile(request, username) -> HttpResponse:
    """Функция для отображения страницы профиля"""
    profile = get_object_or_404(User, username=username)

    if request.user.username == username:
        posts = Post.objects.select_related(
            'category', 'author', 'location'
        ).filter(
            author__username=username,
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    else:
        posts = Post.objects.select_related(
            'category', 'author', 'location'
        ).filter(
            author__username=username,
            pub_date__lt=now(),
            is_published=True,
            category__is_published=True,
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = (
        {'page_obj': page_obj, 'profile': profile}
    )
    return render(request, 'blog/profile.html', context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """CBV для редактирования профиля"""

    model = User
    fields = ['username', 'email', 'first_name', 'last_name']
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    """CBV для создания постов"""

    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """CBV для редактирования постов"""

    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.kwargs['post_id']
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs[self.pk_url_kwarg]},
        )


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """CBV для удаления постов"""

    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'


class AddCommentCreateView(LoginRequiredMixin, CreateView):
    """CBV для создания комментариев"""

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs[self.pk_url_kwarg]}
        )


class EditCommentUpdateView(OnlyAuthorMixin, UpdateView):
    """CBV для редактирования комментариев"""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class DeleteCommentDeleteView(OnlyAuthorMixin, DeleteView):
    """CBV для удаления комментариев"""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
