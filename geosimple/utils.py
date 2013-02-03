import geohash


# Mapping geohash length (in characters) to +/- error size (in kilometres)
GEOHASH_ERROR_SIZES = {
    1: 2500,
    2: 630,
    3: 78,
    4: 20,
    5: 2.4,
    6: 0.61,
    7: 0.076,
    8: 0.019,
}


class Point(object):

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    @property
    def geohash(self):
        return Geohash(geohash.encode(self.latitude, self.longitude))


class Geohash(str):

    _point = None

    @property
    def point(self):
        if not self._point:
            self._point = convert_to_point(geohash.decode(self))
        return self._point

    def expand(self):
        return [Geohash(hash) for hash in geohash.expand(self)]

    def trim(self, length):
        return Geohash(self[0:length])


def convert_to_point(arg):
    """Flexibly convert a range of different types to a Point"""

    # Support objects with "latitude" and "longitude" properties
    try:
        return Point(arg.latitude, arg.longitude)
    except AttributeError:
        pass

    # Support objects with "lat" and "lon" properties
    try:
        return Point(arg.lat, arg.lon)
    except AttributeError:
        pass

    # Support dicts with "latitude" and "longitude" keys
    try:
        return Point(arg["latitude"], arg["longitude"])
    except (KeyError, TypeError):
        pass

    # Support dicts with "lat" and "lon" keys
    try:
        return Point(arg["lat"], arg["lon"])
    except (KeyError, TypeError):
        pass

    # Support (lat, lon) two-tuple
    try:
        lat, lon = arg
        return Point(lat, lon)
    except TypeError:
        pass


def geohash_length_for_error(radius):
    """For a given distance radius in km, return the number of characters
    that a geohash should be trimmed to, ensuring that the resulting
    geohash completely covers the requested radius."""
    for geohash_length, error in GEOHASH_ERROR_SIZES.items():
        if error < radius:
            return geohash_length - 1