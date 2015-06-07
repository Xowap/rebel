# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :
#
# rebel
# (c) 2015 Rémy Sanchez <remy.sanchez@hyperthese.net>

import random

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.conf import settings
from rebel.flickr import FlickrAPI
from rebel.models import FlickrPicture


class Command(BaseCommand):
    help = 'Import meta data of Flickr pictures currently in DB'

    def handle(self, *args, **options):
        flickr = FlickrAPI(settings.FLICKR_API_KEY, None)
        i = 0

        photos = list(FlickrPicture.objects.filter(url=''))
        random.shuffle(photos)

        for photo in photos:
            info = flickr.info(photo.flickr_id)

            if info is not None:
                photo.location = Point(*info['location'])
                photo.title = info['title']
                photo.description = info['description']
                photo.url = info['url']
                photo.save()

            if not i % 100:
                self.stdout.write('.', ending='')
                self.stdout.flush()

            i += 1

        self.stdout.write(' done!')
