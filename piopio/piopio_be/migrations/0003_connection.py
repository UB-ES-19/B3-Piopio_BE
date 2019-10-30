# Generated by Django 2.2.6 on 2019-10-30 19:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('piopio_be', '0002_post'),
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_creator_set', to=settings.AUTH_USER_MODEL)),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
