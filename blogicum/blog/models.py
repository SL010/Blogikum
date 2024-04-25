from django.db import models
from django.contrib.auth import get_user_model

from .constans import MAX_LENGTH_STR

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta():
        abstract = True


class Category(BaseModel):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_STR)
    description = models.TextField('Описание')
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; разрешены '
            'символы латиницы, цифры, дефис и подчёркивание.'
        ),
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(BaseModel):
    name = models.CharField('Название места', max_length=MAX_LENGTH_STR)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Post(BaseModel):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_STR)
    text = models.TextField('Текст')
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в '
            'будущем — можно делать отложенные публикации.'
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )

    class Meta:
        default_related_name = 'posts'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', )


class Comment(models.Model):
    text = models.TextField('Комментарии')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
        default_related_name = 'comments'
