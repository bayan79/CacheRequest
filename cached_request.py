import hashlib
import json
import logging
import dbm
from typing import Any

import requests

FILE_NAME = 'cache.db'
logger = logging.getLogger('CachedRequest')


# ============= STORAGE ==================

class Storage:
    def __init__(self, file: str):
        self.file = file

    def set(self, key, value):
        with dbm.open(self.file, 'w') as db:
            db[key] = value

    def get(self, key):
        with dbm.open(self.file, 'r') as db:
            return db[key]

    def get_or_set(self, key, value):
        with dbm.open(self.file, 'c') as db:
            if key in db:
                return db[key]
            db[key] = value

    def get_or_set_result(self, key, function, dict_args: dict = None):
        with dbm.open(self.file, 'c') as db:
            if key in db:
                return json.loads(db[key])
            args = dict_args or {}
            result = function(**args)
            db[key] = json.dumps(result)
        return result


# ============= CACHE UTILS ==================

def hash_value(value, hash_func=None):
    if hash_func is None:
        def hash_func(_val):
            return hashlib.sha256(str(_val).encode()).hexdigest()

    if not isinstance(value, (dict, list, set)):
        return hash_func(value)

    return json.dumps({k: hash_value(value[k]) for k in value}, sort_keys=True)


def cached(warehouse: Storage):
    def cached_wrapper(request_func):
        def wrapper(method, url, params=None, headers=None, data=None, **kwargs):
            dict_args = {
                'method': method,
                'url': url,
                'params': params,
                'headers': headers,
                'data': data,
            }
            result = warehouse.get_or_set_result(
                key=hash_value(dict_args),
                function=request_func,
                dict_args={**dict_args, **kwargs}
            )
            return result
        return wrapper
    return cached_wrapper


# ============= REQUEST IMPLEMENTATION ==================

storage = Storage(FILE_NAME)


@cached(storage)
def cached_request(method, url, params: dict = None, headers: dict = None, data: Any = None, **kwargs):
    make_request = {
        'GET': requests.get,
        'POST': requests.post
    }.get(method, None)
    if make_request is None:
        raise NotImplementedError(f'Method {method} not implemented yet')

    result = make_request(url, params=params, headers=headers, data=data, **kwargs)
    logger.info(f'Making request: {method} {url} PARAMS={params} HEADERS={headers} DATA={data}')
    return result.json()
