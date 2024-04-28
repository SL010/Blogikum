from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        fields = ('title', 'text', 'pub_date', 'image', 'category')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
