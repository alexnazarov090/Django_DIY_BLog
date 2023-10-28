from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.text import slugify
from django.http import JsonResponse
from django.core import serializers
from django.core.cache import cache
from datetime import date
from django.db.models import Q

from .utils import get_total_num, get_top_contributors, get_most_pop_cats, get_tags
from .models import BlogPost, BlogAuthor, Comment, Tag

import logging

logger = logging.getLogger(__name__)


# function-based views
def index(request):
    """
    A view for an index page describing the site
    """
    total_num = get_total_num()
    top_contributors = get_top_contributors()
    most_pop_cats = get_most_pop_cats()
    tags = get_tags()

    context = {
                'num_of_blog_posts': total_num.blog_posts,
                'num_of_bloggers': total_num.bloggers,
                'num_of_comments': total_num.comments,
                'top_contributors': top_contributors,
                'most_pop_cats': most_pop_cats,
                'tags': tags,
    }

    return render(request, 'blog/index.html', context=context)

def get_related_blogposts(request, word):
    tag = Tag.objects.get(word=word)
    blogposts = tag.blogposts.all()
    context = {'blogposts': blogposts}
    return render(request, 'blog/tags.html', context=context)

def update_like_dislike_count(request, slug):
    """
    A view to update like/dislike count
    """
    clicked_elem_id = request.GET.get('clicked_elem_id')
    blogpost = get_object_or_404(BlogPost, slug=slug)
    blogpost_likes = int(blogpost.likes)
    blogpost_dislikes = int(blogpost.dislikes)

    if len(blogpost.liked_disliked_users) == 0:
        blogpost.liked_disliked_users = dict(liked_users=[], disliked_users=[])
    blogpost_liked_users = blogpost.liked_disliked_users['liked_users']
    blogpost_disliked_users = blogpost.liked_disliked_users['disliked_users']

    if clicked_elem_id == 'blogpost__thumbs-up-btn':
        if str(request.user.id) not in blogpost_liked_users:
            blogpost.likes = str(blogpost_likes + 1)
            blogpost_liked_users.append(str(request.user.id))
        else:
            blogpost.likes = str(blogpost_likes - 1)
            blogpost_liked_users.remove(str(request.user.id))

        if str(request.user.id) in blogpost_disliked_users:
            blogpost_disliked_users.remove(str(request.user.id))
            if blogpost_dislikes > 0:
                blogpost.dislikes = str(blogpost_dislikes - 1)

    elif clicked_elem_id == 'blogpost__thumbs-down-btn':
        if str(request.user.id) not in blogpost_disliked_users:
            blogpost.dislikes = str(blogpost_dislikes + 1)
            blogpost_disliked_users.append(str(request.user.id))
        else:
            blogpost.dislikes = str(blogpost_dislikes - 1)
            blogpost_disliked_users.remove(str(request.user.id))

        if str(request.user.id) in blogpost_liked_users:
            blogpost_liked_users.remove(str(request.user.id))
            if blogpost_likes > 0:
                blogpost.likes = str(blogpost_likes - 1)
    
    blogpost.save(update_tags=False)

    if request.is_ajax and request.method == 'GET':
        ser_blogpost = serializers.serialize('json', [ blogpost, ])
        return JsonResponse({"blogpost": ser_blogpost}, status=200)

def search(request):
    """
    Search related blogposts
    """
    searched_word = request.GET.get("search")

    if searched_word:
        related_blogposts = BlogPost.objects.filter(
                            Q(title__icontains=f"{searched_word}") | 
                            Q(description__icontains=f"{searched_word}"))
    else:
        related_blogposts = {}

    context = {'related_blogposts': related_blogposts, 'searched_word': searched_word}
    return render(request, 'blog/search_results.html', context=context)


# class-based views
class BlogPostListView(generic.ListView):
    """
    A view for a list of all blog posts
    """
    model = BlogPost
    paginate_by = 5

    queryset = BlogPost.objects.order_by('-post_date')


class BlogAuthorListView(generic.ListView):
    """
    A view for a list of all blog authors
    """
    model = BlogAuthor
    template_name = 'blog/blogger_list.html'
    context_object_name = 'blogger_list'

    queryset = BlogAuthor.objects.order_by('username')


class BlogPostDetailView(generic.DetailView):
    """
    A view for a blog post detail view
    """
    model = BlogPost
    context_object_name = 'blogpost'

    def get_context_data(self, **kwargs):
        context = super(BlogPostDetailView, self).get_context_data(**kwargs)
        blogpost = get_object_or_404(BlogPost, slug = self.kwargs['slug'])

        if self.request.user.is_authenticated:
            if self.request.user not in blogpost.viewed_users.all():
                blogpost.viewed_users.add(self.request.user)

        else:
            session_id= self.request.session.session_key
            if session_id and session_id not in blogpost.anonymous_users:
                blogpost.anonymous_users.append(session_id)

        blogpost.views += 1 
        blogpost.save(update_tags=False)
        context['views'] = blogpost.views

        if len(blogpost.liked_disliked_users) == 0:
            blogpost.liked_disliked_users = dict(liked_users=[], disliked_users=[])
        context['is_liked'] = str(self.request.user.id) in blogpost.liked_disliked_users['liked_users']
        context['is_disliked'] = str(self.request.user.id) in blogpost.liked_disliked_users['disliked_users']
        return context


class BlogAuthorDetailView(generic.DetailView):
    """
    A view for a blog author detail view
    """
    model = BlogAuthor
    template_name = 'blog/blogger_detail.html'
    context_object_name = 'blogger'

    def get_context_data(self, **kwargs):
        context = super(BlogAuthorDetailView, self).get_context_data(**kwargs)
        context['blogpost_list'] = BlogPost.objects.filter(author=self.kwargs['pk'])
        return context

class BloggerProfileDetailView(generic.DetailView):
    """
    A view for a blogger profile detail view
    """
    model = BlogAuthor
    template_name = 'blog/blogger_profile.html'
    context_object_name = 'blogger'

    def get_context_data(self, **kwargs):
        context = super(BloggerProfileDetailView, self).get_context_data(**kwargs)
        context['blogpost_list'] = BlogPost.objects.filter(author=self.kwargs['pk'])
        return context


class BloggerProfileCreate(LoginRequiredMixin, CreateView):
    """
    A form to create a blogger profile
    """
    model = BlogAuthor
    fields = ['profile_image', 'bio']
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/bloggerprofile_create_form.html'

    def form_valid(self, form):
        """
        Add user to form data before setting it as valid (so it is saved to model)
        """
        # Make logged-in user a blogger
        if not self.request.user.is_blogger:
            form.instance.username = self.request.user
            self.request.user.is_blogger = True
            self.request.user.save()

        # Call super-class form validation behavior
        return super(BloggerProfileCreate, self).form_valid(form)


class BloggerProfileUpdate(LoginRequiredMixin, UpdateView):
    """
    A form to update a blogger profile
    """
    model = BlogAuthor
    fields = ['profile_image', 'bio']
    template_name = 'blog/bloggerprofile_create_form.html'

    def get_success_url(self):
        blogauthor = BlogAuthor.objects.get(pk=self.kwargs['pk'])
        return reverse('blog:blogger-profile', kwargs={'pk': blogauthor.pk})


class BloggerProfileDelete(LoginRequiredMixin, DeleteView):
    """
    A view to delete a blogger profile
    """
    model = BlogAuthor
    template_name = 'blog/bloggerprofile_delete.html'
    success_url = reverse_lazy('blog:index')


class CommentCreate(LoginRequiredMixin, CreateView):
    """
    A form to create a comment for blogpost
    """
    model = Comment
    fields = ['description']

    def get_success_url(self):
        blogpost = get_object_or_404(BlogPost, slug = self.kwargs['slug'])
        return reverse('blog:blog-detail', kwargs={'slug': blogpost.slug})

    def form_valid(self, form):
        """
        Add author and associated blog to form data before setting it as valid (so it is saved to model)
        """
        #Add logged-in user as author of comment
        form.instance.commenter = self.request.user
        #Associate comment with blog based on passed id
        form.instance.blog=get_object_or_404(BlogPost, slug = self.kwargs['slug'])
        # Call super-class form validation behavior
        return super(CommentCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CommentCreate, self).get_context_data(**kwargs)
        # Get the blogpost object from the "pk" URL parameter and add it to the context
        context['blogpost'] = get_object_or_404(BlogPost, slug = self.kwargs['slug'])
        return context


class CommentUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    A view to update a comment for blogpost
    """
    permission_required = 'blog.change_comment'
    model = Comment
    fields = ['description']
    template_name = 'blog/comment_form.html'

    def get_success_url(self):
        comment = Comment.objects.get(pk=self.kwargs['pk'])
        blogpost = comment.blog
        return reverse('blog:blog-detail', kwargs={'slug': blogpost.slug})


class CommentDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    A view to delete a comment for blogpost
    """
    permission_required = 'blog.delete_comment'
    model = Comment

    def get_success_url(self):
        comment = Comment.objects.get(pk=self.kwargs['pk'])
        blogpost = comment.blog
        return reverse('blog:blog-detail', kwargs={'slug': blogpost.slug})


class BlogPostCreate(LoginRequiredMixin, CreateView):
    """
    A form to create a blogpost
    """
    model = BlogPost
    fields = ['title', 'image', 'description', 'category']
    success_url = reverse_lazy('blog:blogs')

    def form_valid(self, form):
        """
        Add author to form data before setting it as valid (so it is saved to model)
        """
        form.instance.author = BlogAuthor.objects.get(username=self.request.user)
        # Make a slugfield
        form.instance.slug = slugify(str(date.today()) + '-' + form.instance.title, allow_unicode=True)
        # Call super-class form validation behavior
        return super(BlogPostCreate, self).form_valid(form)


class BlogPostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    A view to update a blogpost
    """
    permission_required = 'blog.change_blogpost'
    model = BlogPost
    fields = ['title', 'image', 'description', 'category']
    success_url = reverse_lazy('blog:blogs')


class BlogPostDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    A view to delete a blogpost
    """
    permission_required = 'blog.delete_blogpost'
    model = BlogPost
    success_url = reverse_lazy('blog:blogs')
