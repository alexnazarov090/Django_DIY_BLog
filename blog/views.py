from django.db.models import query
from django.shortcuts import render

from .services import get_total_num, get_top_contributors
from django.views import generic
from .models import BlogPost, BlogAuthor

# Create your views here.
def index(request):
    """
    A view for an index page describing the site
    """
    total_num = get_total_num()
    top_contributors = get_top_contributors()

    context = {
                'num_of_blog_posts': total_num.blog_posts,
                'num_of_bloggers': total_num.bloggers,
                'num_of_comments': total_num.comments,
                'top_contributors': top_contributors
    }

    return render(request, 'blog/index.html', context=context)


class BlogPostListView(generic.ListView):
    """
    A view for a list of all blog posts
    """
    model = BlogPost
    paginate_by = 5

    queryset = BlogPost.objects.order_by('-post_date')


class BlogAuthorDetailView(generic.DetailView):
    """
    A view for a blog author detail view
    """
    model = BlogAuthor