# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :
#
# rebel
# (c) 2015 Rémy Sanchez <remy.sanchez@hyperthese.net>

from django.core.management.base import BaseCommand
from django.conf import settings
from rebel.flickr import FlickrAPI, ChunkIterator
from rebel.models import FlickrPicture


class Command(BaseCommand):
    help = 'Fill the DB with pictures inside the given bbox'

    def add_arguments(self, parser):
        parser.add_argument('bbox', type=float, nargs=4)

    def handle(self, bbox, *args, **options):
        flickr = FlickrAPI(settings.FLICKR_API_KEY, None)

        for photos_it in ChunkIterator(flickr.search(bbox)).chunks(100):
            photos = list(photos_it)
            photos_ids = set(int(x['id']) for x in photos)
            current_ids = set(FlickrPicture.objects
                              .filter(flickr_id__in=photos_ids)
                              .values_list('flickr_id', flat=True))
            missing = photos_ids - current_ids

            FlickrPicture.objects.bulk_create(
                FlickrPicture(flickr_id=x['id']) for x in photos if int(x['id']) in missing
            )

            self.stdout.write('.', ending='')
            self.stdout.flush()

        self.stdout.write(' done!')
