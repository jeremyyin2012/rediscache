"""redis based cache which acts as always empty if redis is not available."""

import pickle
import functools

try:
    from redis import StrictRedis
    from redis import ConnectionError
except ImportError as e:
    class ConnectionError(Exception):
        pass

    class StrictRedis(object):
        def get(self, key):
            raise ConnectionError

        def set(self, key):
            raise ConnectionError

        def setex(self, time, key):
            raise ConnectionError

        def __contains__(self, key):
            raise ConnectionError

__version__ = '0.0.0'


def hashkey(*args, **kwargs):
    t = args
    if kwargs:
        t += sum(sorted(kwargs.items()), ())
    return str(hash(t))


class StrictRedisCache(object):
    def __init__(self, name, ttl=None, **kwargs):
        self.ttl = ttl
        self.name = name
        self._redis = StrictRedis(**kwargs)

    def __getitem__(self, key):
        encoded = self._redis.get(key)
        return pickle.loads(encoded)

    def __setitem__(self, key, value):
        encoded = pickle.dumps(value)
        if self.ttl is None:
            self._redis.set(key, encoded)
        else:
            self._redis.setex(key, self.ttl, encoded)

    def __contains__(self, key):
        return key in self._redis

    def makekey(self, *args, **kwargs):
        return self.name + ':' + hashkey(*args, **kwargs)


class RedisCache(StrictRedisCache):
    def __setitem__(self, key, value):
        try:
            super(RedisCache, self).__setitem__(key, value)
        except ConnectionError:
            pass

    def __contains__(self, key):
        try:
            return super(RedisCache, self).__contains__(key)
        except ConnectionError:
            return False


def cached(cache):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key = cache.makekey(*args, **kwargs)
            if key in cache:
                return cache[key]
            else:
                value = fn(*args, **kwargs)
                cache[key] = value
                return value
        return wrapper
    return decorator
