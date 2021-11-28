from django.http import request
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .services import get_total_num, get_top_contributors
from .models import BlogPost, BlogAuthor, Comment

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
