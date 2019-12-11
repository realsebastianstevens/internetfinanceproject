import sys

from redis import Redis
from rq import Worker, Queue, Connection

from coin.config import Config

conn = Redis.from_url(Config.redis_url())
listen = ['high', 'default', 'low']

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("No port specified")

    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
