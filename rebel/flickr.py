# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :
#
# rebel
# (c) 2015 Rémy Sanchez <remy.sanchez@hyperthese.net>

import requests
import time


ENDPOINT = 'https://api.flickr.com/services/rest/'
QUERY_INTERVAL_SEC = 1.0
PER_PAGE = 250
MAX_TOTAL = 4000


class FlickrAPI(object):
    def __init__(self, key, secret):
        self.key, self.secret = key, secret
        self.last_query = None

    def rate_limit(self):
        now = time.time()

        if self.last_query is not None and now - self.last_query < QUERY_INTERVAL_SEC:
            time.sleep((QUERY_INTERVAL_SEC - now + self.last_query) * 0.01)

        self.last_query = now

    def get(self, method, params=None, **kwargs):
        self.rate_limit()

        if params is None:
            params = {}

        params.update({
            'api_key': self.key,
            'format': 'json',
            'nojsoncallback': 1,
            'method': method,
        })

        return requests.get(ENDPOINT, params=params, **kwargs)

    def location(self, photo_id):
        """
        Returns the (longitude, latitude) location of the specified photo, or None if an error
        occurred.

        :param photo_id:
        :return:
        """

        r = self.get('flickr.photos.geo.getLocation', {
            'photo_id': photo_id,
        }).json()

        if r['stat'] == 'ok':
            return (float(r['photo']['location']['longitude']),
                    float(r['photo']['location']['latitude']))

    def info(self, photo_id):
        r = self.get('flickr.photos.getInfo', {
            'photo_id': photo_id,
        }).json()

        if r['stat'] == 'ok':
            return {
                'location': (float(r['photo']['location']['longitude']),
                             float(r['photo']['location']['latitude'])),
                'title': r['photo']['title'].get('_content', ''),
                'description': r['photo']['description'].get('_content', ''),
                'url': r['photo']['urls']['url'][0]['_content'],
            }

    def search(self, bbox):
        """
        This function returns all pictures found within a bounding box. If the bounding box returns
        too many results (more than 4000), it will automatically be divided in order to be able to
        fetch all the results.

        Within a call, a single picture is guaranteed to be returned only once.

        :param bbox:
        :return:
        """

        pic_ids = set()

        def split_bbox(big_bbox, n):
            x_1, y_1, x_2, y_2 = big_bbox

            w = (x_2 - x_1) / n
            h = (y_2 - y_1) / n

            for i in range(0, n):
                for j in range(0, n):
                    yield (
                        x_1 + w * i,
                        y_1 + h * j,
                        x_1 + w * (i + 1),
                        y_1 + h * (j + 1),
                    )

        def find_bbox_splits(candidate_bbox):
            for sub_bbox in split_bbox(candidate_bbox, 2):
                r = get_photos(1, sub_bbox)
                c = int(r['photos']['total'])

                if c > MAX_TOTAL:
                    yield from find_bbox_splits(sub_bbox)
                else:
                    yield sub_bbox

        def check_response(r):
            valid = 'photos' in r \
                    and 'pages' in r['photos'] \
                    and 'stat' in r \
                    and r['stat'] == 'ok'

            if not valid:
                return False

            new_ids = set(x['id'] for x in r['photos']['photo'])
            return len(new_ids - pic_ids) > 0

        def yield_photos(result):
            for photo in result['photos']['photo']:
                if photo['id'] not in pic_ids:
                    pic_ids.add(photo['id'])
                    yield photo

        def get_photos(page, sub_bbox):
            return self.get('flickr.photos.search', {
                'perpage': PER_PAGE,
                'bbox': ','.join(str(x) for x in sub_bbox),
                'page': page,
            }).json()

        def get_sub(sub_bbox):
            r = get_photos(1, sub_bbox)
            if check_response(r):
                yield from yield_photos(r)

                for page in range(2, r['photos']['pages'] + 1):
                    r = get_photos(page, sub_bbox)

                    if check_response(r):
                        yield from yield_photos(r)
                    else:
                        break

        def get_all():
            for sub_bbox in find_bbox_splits(bbox):
                yield from get_sub(sub_bbox)

        yield from get_all()


class ChunkIterator(object):
    """
    This iterator cuts down an iterator into several chunks. By example, you can iterate over
    a very long list and do chunk creates every 1000 entry using this.
    """
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.iterating = True
        self._next = None

        self.next()

    def next(self):
        nxt = self._next

        try:
            self._next = next(self.iterator)
        except StopIteration:
            self.iterating = False

        return nxt

    def chunks(self, size):
        """
        Call this method to return the chunks iterator

        :param size: int, size of a chunk
        :return:
        """

        def iter_chunk():
            for i in range(0, size):
                yield self.next()

                if not self.iterating:
                    break

        while self.iterating:
            yield iter_chunk()
