# Generated by Django 3.2.9 on 2021-11-21 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20211121_2148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='slug',
            field=models.SlugField(max_length=100, unique=True),
        ),
    ]
