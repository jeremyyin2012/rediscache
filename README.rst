This module provides simple redis based persitent cache decorators. If redis is
not availble, they will simply do nothing.

There are two decorators: ``@cached`` for functions and ``@async_cached`` for
coroutines::

    import asyncio
    import aiohttp
    from rediscache import async_cached

    @async_cached('test', ttl=100, port=6379)
    @asyncio.coroutine
    def test(url):
        data = yield from aiohttp.get('http://python.org')
        return data
