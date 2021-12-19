from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('blogs/', views.BlogPostListView.as_view(), name='blogs'),
    path('bloggers/', views.BlogAuthorListView.as_view(), name='bloggers'),
    path('blog/<slug:slug>', views.BlogPostDetailView.as_view(), name='blog-detail'),
    path('blogger/<int:pk>', views.BlogAuthorDetailView.as_view(), name='blogger-detail'),
    path('blogger-profile/<int:pk>', views.BloggerProfileDetailView.as_view(), name='blogger-profile'),
    path('create-blogpost', views.BlogPostCreate.as_view(), name='blogpost-create'),
    path('<slug:slug>/update-blogpost', views.BlogPostUpdate.as_view(), name='blogpost-update'),
    path('<slug:slug>/delete-blogpost', views.BlogPostDelete.as_view(), name='blogpost-delete'),
    path('create-blogger-profile', views.BloggerProfileCreate.as_view(), name='blogger-profile-create'),
    path('blogger-profile/<int:pk>/update-blogger-profile', views.BloggerProfileUpdate.as_view(), name='blogger-profile-update'),
    path('blog/<slug:slug>/create', views.CommentCreate.as_view(), name='comment-create'),
    path('blog/<slug:slug>/comment/<int:pk>/update', views.CommentUpdate.as_view(), name='comment-update'),
    path('blog/<slug:slug>/comment/<int:pk>/delete', views.CommentDelete.as_view(), name='comment-delete'),
    path('signup', views.signup, name='signup'),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]
