# File: mini_insta/migrations/0007_profile_user.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 10/23/2026
# Description: Connect existing profiles to the default admin account.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Add ownership without removing any existing profiles."""

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mini_insta', '0006_follow_comment_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
