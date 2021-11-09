from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BlogPost, BlogAuthor, Comment

# Register your models here.
admin.site.register(User, UserAdmin)


class CommentsInline(admin.TabularInline):
    model = Comment
    extra = 0

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'post_date', 'author', 'description')
    fields = ['title', ('author', 'post_date'), 'description']
    list_filter = ('author',)

    inlines = [CommentsInline]


class BlogPostsInline(admin.TabularInline):
    model = BlogPost
    extra = 0

@admin.register(BlogAuthor)
class BlogAuthorAdmin(admin.ModelAdmin):
    list_display = ('username', 'bio')

    inlines = [BlogPostsInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post_date', 'commenter', 'description', 'blog')
    fields = [('commenter', 'post_date'), 'description', 'blog']
    list_filter = ('commenter', 'blog')

