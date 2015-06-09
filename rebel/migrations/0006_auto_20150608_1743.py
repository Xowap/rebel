# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rebel', '0005_flickrpicture_raw'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flickrpicture',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(
                srid=4326,
                db_index=True,
                null=True
            ),
        ),
    ]
