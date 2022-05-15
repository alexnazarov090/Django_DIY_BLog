from collections import namedtuple
import re
import nltk
import os
from django.db.models import Count
from django.core.cache import cache
from .models import BlogAuthor, BlogPost, Comment

import logging

logger = logging.getLogger(__name__)

CURRENT_WORKING_DIR = os.getcwd()
logger.info(CURRENT_WORKING_DIR)

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

def get_most_frequent_words():
    """
    Get a list of most frequently used words
    """
    frequent_words = {}
    word_urls = {}
    download_dir = os.path.join(f'{CURRENT_WORKING_DIR}', 'nltk_data')
    nltk.download('punkt', download_dir=download_dir)
    nltk.download('averaged_perceptron_tagger', download_dir=download_dir)
    regex = r'\w{2,}'
    blogposts = BlogPost.objects.all()

    for blogpost in blogposts:
        bp_desc = blogpost.description
        tokens = nltk.word_tokenize(bp_desc)
        tagged = nltk.pos_tag(tokens)
        for word, tag in tagged:
            if tag.startswith('N') and re.search(regex, word):
                frequent_words[word] = frequent_words.get(word, 0) + 1
                word_urls[word] = word_urls.get(word, set())
                word_urls[word].add(blogpost)
    
    frequent_words_list = sorted(frequent_words, key=frequent_words.get, reverse=True)[:30]

    for word in frequent_words_list:
        cache.set(word, word_urls[word])
        
    return frequent_words_list
