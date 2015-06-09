# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :
#
# rebel
# (c) 2015 Rémy Sanchez <remy.sanchez@hyperthese.net>

import json
import time

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.conf import settings
from rebel.flickr import FlickrAPI, ChunkIterator, BaseBboxExplorer
from rebel.models import FlickrPicture, BboxProgression


class Command(BaseCommand):
    help = 'Fill the DB with pictures inside the given bbox'

    def add_arguments(self, parser):
        parser.add_argument('bbox', type=float, nargs=4)

    def handle(self, bbox, *args, **options):
        flickr = FlickrAPI(settings.FLICKR_API_KEY, None)
        explorer = BboxExplorer()
        extras = ['description', 'date_taken', 'geo']

        while True:
            try:
                for photos_it in ChunkIterator(flickr.search(bbox, explorer, extras)).chunks(100):
                    photos = list(photos_it)
                    photos_ids = set(int(x['id']) for x in photos)
                    current_ids = set(FlickrPicture.objects
                                      .filter(flickr_id__in=photos_ids)
                                      .values_list('flickr_id', flat=True))
                    missing = photos_ids - current_ids

                    FlickrPicture.objects.bulk_create(
                        FlickrPicture(
                            flickr_id=x['id'],
                            owner_id=x['owner'],
                            title=x['title'],
                            description=x['description'].get('_content'),
                            location=Point(float(x['longitude']), float(x['latitude'])),
                            url='https://www.flickr.com/photos/{user_id}/{photo_id}'.format(
                                user_id=x['owner'],
                                photo_id=x['id'],
                            ),
                            raw=json.dumps(x),
                        )
                        for x in photos if int(x['id']) in missing
                    )

                    self.stdout.write('.', ending='')
                    self.stdout.flush()

                self.stdout.write(' done!')
                break
            except KeyboardInterrupt:
                self.stdout.write('\nAll right, going away.')
                break
            except ValueError:
                time.sleep(1)


class BboxExplorer(BaseBboxExplorer):
    def progression(self, bbox):
        try:
            x1, y1, x2, y2 = bbox
            p = BboxProgression.objects.get(x1=x1, y1=y1, x2=x2, y2=y2)
            return p.count, p.done
        except BboxProgression.DoesNotExist:
            return None, False

    def explore(self, bbox, count, done):
        x1, y1, x2, y2 = bbox
        p, _ = BboxProgression.objects.get_or_create(x1=x1, y1=y1, x2=x2, y2=y2, defaults={
            'count': count,
        })

        BboxProgression.objects.filter(pk=p.pk).update(
            count=count,
            done=done,
        )
