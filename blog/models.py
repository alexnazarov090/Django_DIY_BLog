from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.fields import SlugField
from django.db.models.fields.related import OneToOneField
from django.urls import reverse
from django.utils.text import slugify

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


# Create your models here.

class User(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    is_blogger = models.BooleanField(default=False)


class BlogPost(models.Model):
    """A class defining a blog model"""

    # Fields
    title = models.CharField(max_length=100, help_text='Enter a name for a blog post')
    post_date = models.DateField(auto_now=True)
    author = models.ForeignKey('BlogAuthor', on_delete=models.SET_NULL, null=True)
    description = models.TextField(help_text='Type in blog post content')
    slug = SlugField(max_length=100, null=False, unique=True)
    likes = models.CharField(max_length=10, default='0')
    dislikes = models.CharField(max_length=10, default='0')
    liked_disliked_users = models.JSONField(null=False, default=dict)
    image = models.ImageField(upload_to='blog/images', default='blog/images/blog-default-image.jpg', null=True)


    # Metadata
    class Meta:
        ordering = ['-post_date']

    # Methods
    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(str(self.post_date) + '-' + self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns the url to access a particular instance of Blog post."""
        return reverse('blog:blog-detail', kwargs={'slug': self.slug})

    def __str__(self):
        """String for representing the Blog object (in Admin site etc.)."""
        return self.title


class BlogAuthor(models.Model):
    """A class defining a blog author model"""

    # Fields
    username = OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=1000, help_text='Blog author biography', null=True)
    profile_image = models.ImageField(upload_to='blog/images', default='blog/images/default.png', null=True)
    profile_image_thumbnail = ImageSpecField(source='profile_image',
                                            processors=[ResizeToFill(100, 100)],
                                            format='PNG',
                                            options={'quality': 60})

    # Methods
    def get_absolute_url(self):
        """Returns the url to access a particular instance of Blog Author(Blogger)."""
        return reverse('blog:blogger-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Blogger object (in Admin site etc.)."""
        return str(self.username)


class Comment(models.Model):
    """A class defining a comment model"""

    # Fields
    post_date = models.DateTimeField(auto_now=True)
    description = models.TextField(max_length=1000, help_text='Enter a comment description')
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE, null=True, blank=True)
    commenter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Metadata
    class Meta:
        ordering = ['post_date']

    def __str__(self):
        """String for representing the Comment object (in Admin site etc.)."""
        if len(self.description) >= 75:
            return self.description[0:75]
        return self.description
