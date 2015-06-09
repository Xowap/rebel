# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :
#
# rebel
# (c) 2015 Rémy Sanchez <remy.sanchez@hyperthese.net>

from django.db import models
from django.contrib.gis.db import models as geo_models


class FlickrPicture(models.Model):
    flickr_id = models.BigIntegerField(unique=True)
    owner_id = models.TextField(blank=True, default='')
    location = geo_models.PointField(null=True, spatial_index=True, db_index=True)
    title = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    url = models.URLField(blank=True, default='')
    raw = models.TextField(null=True)

    objects = geo_models.GeoManager()


class BboxProgression(models.Model):
    x1 = models.FloatField()
    y1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()
    count = models.IntegerField()
    done = models.BooleanField(default=False)

    class Meta:
        unique_together = ('x1', 'y1', 'x2', 'y2')
