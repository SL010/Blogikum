from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest, Http404
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.utils.timezone import now
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from blog.forms import PostForm, CommentForm
from blog.query_posts import get_posts
from blog.mixins import OnlyAuthorMixin, ChangeCommentMixin
from blog.models import Post, Category, Comment
from blog.paginator import paginator


User = get_user_model()


def index(request: HttpRequest) -> HttpResponse:
    """Функция отображает посты на главной странице"""
    post_list = get_posts(filtration=True, annotation=True)
    page_obj = paginator(request, post_list)
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
    post_list = get_posts(
        manager=category.posts,
        filtration=True,
        annotation=True
    )
    page_obj = paginator(request, post_list)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


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

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user != post.author and (
                not post.is_published
                or not post.category.is_published
                or post.pub_date > now()
        ):
            raise Http404
        return post


def profile(request, username) -> HttpResponse:
    """Функция для отображения страницы профиля"""
    profile = get_object_or_404(User, username=username)

    if request.user.username == username:
        posts = get_posts(manager=profile.posts, annotation=True)
    else:
        posts = get_posts(annotation=True).filter(
            author__username=username,
            category__is_published=True,
        )
    page_obj = paginator(request, posts)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['form'] = PostForm(instance=post)
        return context


class AddCommentCreateView(LoginRequiredMixin, CreateView):
    """CBV для создания комментариев"""

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post, pk=self.kwargs[self.pk_url_kwarg]
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs[self.pk_url_kwarg]}
        )


class EditCommentUpdateView(ChangeCommentMixin, UpdateView):
    """CBV для редактирования комментариев"""

    form_class = CommentForm


class DeleteCommentDeleteView(ChangeCommentMixin, DeleteView):
    """CBV для удаления комментариев"""

    pass


class ReqistrationCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')
