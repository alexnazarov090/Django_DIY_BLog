from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import login, authenticate
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.text import slugify
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_protect
from datetime import date

from .services import get_total_num, get_top_contributors
from .models import User, BlogPost, BlogAuthor, Comment
from .forms import SignUpForm
from .tokens import account_activation_token

import logging

logger = logging.getLogger(__name__)

# Create your views here.
# function-based views
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


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            user.is_active = False
            user.save()
            if user.is_authenticated:
                current_site = get_current_site(request)
                subject = 'Activate Your Blog Account'
                message = render_to_string('registration/account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                user.email_user(subject, message)
                return redirect(reverse('account_activation_sent'))
            return redirect(reverse('blog:index'))
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def account_activation_sent(request):
    return render(request, 'registration/account_activation_sent.html')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        return redirect(reverse('blog:index'))
    else:
        return render(request, 'registration/account_activation_invalid.html')


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
    
    logger.info(blogpost.liked_disliked_users)
    blogpost.save()

    if request.is_ajax and request.method == 'GET':
        ser_blogpost = serializers.serialize('json', [ blogpost, ])
        return JsonResponse({"blogpost": ser_blogpost}, status=200)


def validate_username(request):
    """
    A view to check username and email address
    """
    if request.is_ajax and request.method == 'GET':
        username = request.GET.get('username')
        data = {}.fromkeys(('valid', 'error_message'))
        data['valid'] = True

        if User.objects.filter(username__iexact=username).exists():
            data['valid'], data['error_message'] = False, 'A user with this username already exists!'

        return JsonResponse(data, status=200)


def validate_email(request):
    """
    A view to check username and email address
    """
    if request.is_ajax and request.method == 'GET':
        email = request.GET.get('email')
        data = {}.fromkeys(('valid', 'error_message'))
        data['valid'] = True

        if User.objects.filter(email__iexact=email).exists():
            data['valid'], data['error_message'] = False, 'A user with this email already exists!'

        return JsonResponse(data, status=200)


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
    fields = ['title', 'description']
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
    fields = ['title', 'description']
    success_url = reverse_lazy('blog:blogs')


class BlogPostDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    A view to delete a blogpost
    """
    permission_required = 'blog.delete_blogpost'
    model = BlogPost
    success_url = reverse_lazy('blog:blogs')
