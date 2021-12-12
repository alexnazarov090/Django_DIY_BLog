from django.http import request
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
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

from .services import get_total_num, get_top_contributors
from .models import User, BlogPost, BlogAuthor, Comment
from .forms import SignUpForm
from .tokens import account_activation_token


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
                message = render_to_string('blog/account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                user.email_user(subject, message)
                return redirect(reverse('blog:account_activation_sent'))
            return redirect(reverse('blog:index'))
    else:
        form = SignUpForm()
    return render(request, 'blog/signup.html', {'form': form})

def account_activation_sent(request):
    return render(request, 'blog/account_activation_sent.html')

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
        return render(request, 'blog/account_activation_invalid.html')


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


class BlogAuthorDetailView(generic.DetailView):
    """
    A view for a blog author detail view
    """
    model = BlogAuthor
    template_name = 'blog/blogger_detail.html'
    context_object_name = 'blogger'

    def get_context_data(self, **kwargs):
        context = super(BlogAuthorDetailView, self).get_context_data(**kwargs)
        context['blogpost_list'] = get_list_or_404(BlogPost.objects.filter(author=self.kwargs['pk']))
        return context


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
