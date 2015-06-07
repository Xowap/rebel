# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rebel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='flickrpicture',
            name='description',
            field=models.TextField(default='', blank=True),
        ),
        migrations.AddField(
            model_name='flickrpicture',
            name='title',
            field=models.TextField(default='', blank=True),
        ),
        migrations.AddField(
            model_name='flickrpicture',
            name='url',
            field=models.URLField(default='', blank=True),
        ),
    ]
