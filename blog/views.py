from django.http.response import HttpResponse
from django.shortcuts import render
from .models import BlogAuthor, BlogPost, Comment


# Create your views here.
def index(request):
    # Number of blog posts
    num_of_blog_posts = BlogPost.objects.count()

    # Number of blog authors
    num_of_bloggers = BlogAuthor.objects.count()

    # Number of comments
    num_of_comments = Comment.objects.count()

    context = {
                'num_of_blog_posts': num_of_blog_posts,
                'num_of_bloggers': num_of_bloggers,
                'num_of_comments': num_of_comments
    }


    return render(request, 'blog/index.html', context=context)
