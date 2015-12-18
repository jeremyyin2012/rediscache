"""redis based cache which acts as always empty if redis is not available."""

import asyncio
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

        def set(self, key, value):
            raise ConnectionError

        def setex(self, key, time, value):
            raise ConnectionError

        def __contains__(self, key):
            raise ConnectionError

__version__ = '0.0.0'


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
        return self.name.encode('utf8') + b':' + pickle.dumps((args, kwargs))


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


def get_cache(*args, **kwargs):
    if not kwargs and len(args) == 1 and isinstance(args[0], RedisCache):
        return args[0]
    else:
        return RedisCache(*args, **kwargs)


def cached(*args, **kwargs):
    cache = get_cache(*args, **kwargs)
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


def async_cached(*args, **kwargs):
    cache = get_cache(*args, **kwargs)
    def decorator(fn):
        @functools.wraps(fn)
        @asyncio.coroutine
        def wrapper(*args, **kwargs):
            key = cache.makekey(*args, **kwargs)
            if key in cache:
                return cache[key]
            else:
                value = yield from fn(*args, **kwargs)
                cache[key] = value
                return value
        return wrapper
    return decorator
