# Generated by Django 3.2.9 on 2021-11-21 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_comment_blog'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='post_date',
            field=models.DateField(auto_now=True),
        ),
    ]
