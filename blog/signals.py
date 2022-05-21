from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from blog.models import BlogAuthor, BlogPost
from .utils import update_tags, delete_tags


@receiver(post_delete, sender=BlogAuthor)
def delete_blogger_status(sender, instance, **kwargs):
    instance.username.is_blogger = False
    instance.username.save()

@receiver(post_save, sender=BlogPost)
def manage_tags_post_save(sender, instance, **kwargs):
    update_tags()

@receiver(post_delete, sender=BlogPost)
def manage_tags_post_delete(sender, instance, **kwargs):
    delete_tags(instance)
    update_tags()
