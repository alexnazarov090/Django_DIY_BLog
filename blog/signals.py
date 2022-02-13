from django.db.models.signals import post_delete
from django.dispatch import receiver
from blog.models import BlogAuthor, User


@receiver(post_delete, sender=BlogAuthor)
def delete_blogger_status(sender, instance, **kwargs):
    instance.username.is_blogger = False
    instance.username.save()