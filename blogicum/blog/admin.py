from django.contrib import admin

from .models import Category, Location, Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'author', 'text', 'created_at',
        'category', 'pub_date', 'location', 'is_published'
    )
    search_fields = ('text', )
    list_display_links = ('title', )
    list_editable = ('category', 'is_published', 'location')
    list_filter = ('created_at', )
    empty_value_display = '-'


admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
