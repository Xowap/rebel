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
MAX_DEPTH = 20


class FlickrAPI(object):
    def __init__(self, keys, secret):
        self.keys, self.secret = keys, secret
        self.key_index = 0
        self.last_query = None

    def rate_limit(self):
        now = time.time()
        interval = QUERY_INTERVAL_SEC / len(self.keys)

        if self.last_query is not None and now - self.last_query < interval:
            time.sleep((interval - now + self.last_query) * 0.01)

        self.last_query = now

    def get(self, method, params=None, **kwargs):
        self.rate_limit()

        if params is None:
            params = {}

        key = self.keys[self.key_index % len(self.keys)]
        self.key_index += 1

        params.update({
            'api_key': key,
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
        try:
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
                    'owner': r['photo']['owner']['nsid'],
                    'raw': r['photo'],
                }
        except (TypeError, ValueError, KeyError, IndexError, IOError):
            pass

    def search(self, bbox, explorer, extras=None):
        """
        This function returns all pictures found within a bounding box. If the bounding box returns
        too many results (more than 4000), it will automatically be divided in order to be able to
        fetch all the results.

        Within a call, a single picture is guaranteed to be returned only once.

        :param bbox:
        :param explorer: BaseBboxExplorer
        :return:
        """

        pic_ids = set()

        if extras is None:
            extras = []

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

        def find_bbox_splits(candidate_bbox, depth=0):
            for sub_bbox in split_bbox(candidate_bbox, 2):
                count, done = explorer.progression(sub_bbox)

                if not done:
                    if count is None:
                        r = get_photos(1, sub_bbox)
                        c = int(r['photos']['total'])
                        explorer.explore(sub_bbox, c, False)
                    else:
                        c = count

                    if c > MAX_TOTAL and depth < MAX_DEPTH:
                        yield from find_bbox_splits(sub_bbox, depth + 1)
                    else:
                        yield sub_bbox

                    explorer.explore(sub_bbox, c, True)

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
                'extras': ','.join(extras)
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


class BaseBboxExplorer(object):
    def progression(self, bbox):
        raise NotImplementedError

    def explore(self, bbox, count, done):
        raise NotImplementedError


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
