from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.fields import SlugField
from django.db.models.fields.related import OneToOneField
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.sessions.models import Session

from uuid import uuid4
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Thumbnail, ResizeToFit
from tinymce.models import HTMLField


# Create your models here.

class User(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    is_blogger = models.BooleanField(default=False)


class BlogPost(models.Model):
    """A class defining a blog model"""

    # Fields
    title = models.CharField(max_length=100, help_text='Enter a name for a blog post')
    post_date = models.DateField(auto_now_add=True)
    author = models.ForeignKey('BlogAuthor', on_delete=models.SET_NULL, null=True)
    description = HTMLField(help_text='Type in blog post content')
    slug = SlugField(max_length=100, null=False, unique=True)
    likes = models.CharField(max_length=10, default='0')
    dislikes = models.CharField(max_length=10, default='0')
    liked_disliked_users = models.JSONField(null=False, default=dict)
    viewed_users = models.ManyToManyField(User, blank=True)
    views = models.IntegerField(default=0)
    anonymous_users = models.JSONField(null=False, default=list)
    image = models.ImageField(upload_to='blog/images', default='blog/images/blog-default-image.jpg', null=True)
    image_thumbnail = ImageSpecField(source='image',
                                    processors=[ResizeToFit(500, 300)],
                                    format='JPEG',
                                    options={'quality': 60})

    BLOGPOST_CATEGORIES = (
        ('Music', 'Music'),
        ('Fashion', 'Fashion'),
        ('Car', 'Car'),
        ('Travel', 'Travel'),
        ('Technology', 'Technology'),
        ('Movies', 'Movies'),
        ('History', 'History'),
        ('Lifestyle', 'Lifestyle'),
        ('Overall', 'Overall'),
    )

    category = models.CharField(
        max_length=20,
        choices=BLOGPOST_CATEGORIES,
        blank=True,
        default='OV',
        help_text='Blogpost category',
    )


    # Metadata
    class Meta:
        ordering = ['-post_date']

    # Methods
    def save(self, update_tags=True, *args, **kwargs):
        self.slug = self.slug or slugify(str(self.post_date) + '-' + self.title, allow_unicode=True)

        self._update_tags = update_tags

        super().save(*args, **kwargs)

    def display_viewed_users(self):
        return ', '.join(user.username for user in self.viewed_users.all())
    display_viewed_users.short_description = 'Viewed users'

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
    post_date = models.DateTimeField(auto_now_add=True)
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


def get_default_uuid():
    return uuid4().hex

class Tag(models.Model):
    """A class defining a tag model"""

    # Fields
    word = models.CharField(max_length=20, unique=True, default=get_default_uuid)
    blogposts = models.ManyToManyField(BlogPost, blank=True)
    quantity = models.IntegerField(default=0)

    def display_blogposts(self):
        return ', '.join(str(blogpost) for blogpost in self.blogposts.all())
    display_blogposts.short_description = 'Related blogposts'

    def __str__(self):
        """String for representing the Tag object (in Admin site etc.)."""
        return str(self.word)
