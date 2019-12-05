# Generated by Django 2.2.5 on 2019-12-01 18:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('piopio_be', '0002_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='blocked_users',
            field=models.ManyToManyField(related_name='_user_blocked_users_+', to=settings.AUTH_USER_MODEL),
        ),
    ]
