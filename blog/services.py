from collections import namedtuple
from django.db.models import Count
from .models import BlogAuthor, BlogPost, Comment


def get_total_num():
    """
    Get total number of blog posts, bloggers and comments
    return a named tuple of numbers
    """
    
    TotalNumber = namedtuple("TotalNumber", ['blog_posts', 'bloggers', 'comments'])

    # Number of blog posts
    num_of_blog_posts = BlogPost.objects.count()
    # Number of blog authors
    num_of_bloggers = BlogAuthor.objects.count()
    # Number of comments
    num_of_comments = Comment.objects.count()

    total_num = TotalNumber(num_of_blog_posts, num_of_bloggers, num_of_comments)

    return total_num

def get_top_contributors():
    """
    Get a list of top contributors
    """
    top_contributors_list = BlogAuthor.objects.annotate(
                            num_blog_posts=Count('blogpost')).order_by('-num_blog_posts')[:5]

    top_contributors = {contributor: contributor.num_blog_posts for contributor in top_contributors_list}

    return top_contributors

def get_most_pop_cats():
    """
    Get a list of most popular categories
    """
    most_pop_cats = {}
    blogposts = BlogPost.objects.all()

    for blogpost in blogposts:
        most_pop_cats[blogpost.category] = most_pop_cats.get(blogpost.category, 0) + 1
    
    return sorted(most_pop_cats, key=most_pop_cats.get, reverse=True)