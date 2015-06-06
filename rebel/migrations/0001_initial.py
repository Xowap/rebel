# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FlickrPicture',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    primary_key=True,
                    serialize=False,
                    auto_created=True,
                )),
                ('flickr_id', models.BigIntegerField(unique=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
            ],
        ),
    ]
