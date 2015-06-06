# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :
#
# rebel
# (c) 2015 Rémy Sanchez <remy.sanchez@hyperthese.net>

from django.db import models
from django.contrib.gis.db import models as geo_models


class FlickrPicture(models.Model):
    flickr_id = models.BigIntegerField(unique=True)
    location = geo_models.PointField(null=True)

    objects = geo_models.GeoManager()
