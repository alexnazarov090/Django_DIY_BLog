from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BlogPost, BlogAuthor, Comment

# Register your models here.
class CustomUserAdmin(UserAdmin):
    UserAdmin.list_display += ('email_confirmed', 'is_blogger')
    UserAdmin.list_filter += ('email_confirmed', 'is_blogger')
    UserAdmin.fieldsets += (
        ('Personal info', {'fields': ('email_confirmed', )}),
        (None, {'fields': ('is_blogger', )}),
    )

admin.site.register(User, CustomUserAdmin)


class CommentsInline(admin.TabularInline):
    model = Comment
    extra = 0

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('slug',
                    'title',
                    'image',
                    'post_date',
                    'author',
                    'category',
                    'views',
                    'display_viewed_users',
                    'likes',
                    'dislikes',
                    'liked_disliked_users')
    fields = ['title', 'image', 'author', 'description', 'category']
    list_filter = ('author',)
    exclude = ('slug',)

    inlines = [CommentsInline]


class BlogPostsInline(admin.TabularInline):
    model = BlogPost
    extra = 0

@admin.register(BlogAuthor)
class BlogAuthorAdmin(admin.ModelAdmin):
    list_display = ('username', 'profile_image', 'bio')

    inlines = [BlogPostsInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'post_date', 'commenter', 'description', 'blog')
    fields = ['commenter', 'description', 'blog']
    list_filter = ('commenter', 'blog')
