# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rebel', '0003_flickrpicture_owner_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='BboxProgression',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    primary_key=True,
                    serialize=False,
                    auto_created=True
                )),
                ('x1', models.FloatField()),
                ('y1', models.FloatField()),
                ('x2', models.FloatField()),
                ('y2', models.FloatField()),
                ('count', models.IntegerField()),
                ('done', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='bboxprogression',
            unique_together=set([('x1', 'y1', 'x2', 'y2')]),
        ),
    ]
