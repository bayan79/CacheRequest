from cached_request import cached_request
import logging

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    res = cached_request('GET', 'http://worldtimeapi.org/api/timezone/Europe/Paris')
    print(res)
