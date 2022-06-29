from collections import namedtuple
import re
import nltk
import os
import logging
import html

from django.db.models import Count
from django.core.cache import cache

from .models import BlogAuthor, BlogPost, Comment, Tag


logger = logging.getLogger(__name__)

CURRENT_WORKING_DIR = os.getcwd()


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

def get_tags():
    """
    Get a list of most frequently used words
    """
    tags = Tag.objects.all().order_by('-quantity', 'word')[:30]

    return tags

def replace_html_entities(match):
    """
    Replace html entities with unicode chars, eg. &rsquo;
    """
    match = match.group(0)
    return html.unescape(match)

def update_tags():
    """
    Update a list of most frequently used words
    """
    frequent_words = {}
    blogpost_dict = {}
    blogposts = BlogPost.objects.all()

    # download_dir = os.path.join(f'{CURRENT_WORKING_DIR}', 'nltk_data')

    # nltk.download('punkt', download_dir=download_dir)
    # nltk.download('averaged_perceptron_tagger', download_dir=download_dir)

    for blogpost in blogposts:
        bp_desc = re.sub(r'<[^<]+?>', '', blogpost.description , flags=re.MULTILINE) # strip html tags, eg. <p></p>
        cleaned_bp_desc = re.sub(r"(&\S+;)", replace_html_entities, bp_desc) # replace html entities with unicode chars, eg. &rsquo;
        tokens = nltk.word_tokenize(cleaned_bp_desc)
        tagged = nltk.pos_tag(tokens)
        for word, tg in tagged:
            if tg.startswith('N') and re.search(r'\w{2,}', word):
                frequent_words[word] = frequent_words.get(word, 0) + 1
                blogpost_dict[word] = blogpost_dict.get(word, set())
                blogpost_dict[word].add(blogpost)

    frequent_words_list = sorted(frequent_words, key=frequent_words.get, reverse=True)[:30]

    for word in frequent_words_list:
        tag, created = Tag.objects.get_or_create(word=word)

        for bp in blogpost_dict[word]:
            if not bp in tag.blogposts.all():
                tag.blogposts.add(bp)
        tag.quantity = frequent_words[word]
        tag.save()

def delete_tags(blogpost):
    """
    Delete tags if necessary
    """
    # download_dir = os.path.join(f'{CURRENT_WORKING_DIR}', 'nltk_data')

    # nltk.download('punkt', download_dir=download_dir)
    # nltk.download('averaged_perceptron_tagger', download_dir=download_dir)

    regex = r'\w{2,}'

    bp_desc = blogpost.description
    tokens = nltk.word_tokenize(bp_desc)
    tagged = nltk.pos_tag(tokens)
    for word, tg in tagged:
        if tg.startswith('N') and re.search(regex, word):
            if Tag.objects.filter(word__exact=word).exists():
                tag = Tag.objects.get(word__exact=word)
                tag.quantity -= 1
                tag.save()
                if tag.quantity == 0:
                    tag.delete()
