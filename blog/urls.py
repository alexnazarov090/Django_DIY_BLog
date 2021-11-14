from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('blogs/', views.BlogPostListView.as_view(), name='blogs'),
    path('bloggers/', views.BlogAuthorListView.as_view(), name='bloggers'),
    path('blog/<int:pk>', views.BlogPostDetailView.as_view(), name='blog-detail'),
    path('blogger/<int:pk>', views.BlogAuthorDetailView.as_view(), name='blogger-detail'),
    path('blog/<int:pk>/create', views.CommentCreate.as_view(), name='comment-create'),
]
