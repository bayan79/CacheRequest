## A simple module to perform cached requests

Usage example is in `main.py`

Perform request caching by METHOD, URL, PARAMS, HEADERS and DATA values of the request.

Assumed that:
1. METHOD and URL are `str` instance.
2. PARAMS, HEADERS and DATA are `dict` instance.
3. Requests returns JSON response.

Module uses SHA256 hash func to generate key and store JSON response with `dbm` 