# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rebel', '0004_auto_20150608_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='flickrpicture',
            name='raw',
            field=models.TextField(null=True),
        ),
    ]
