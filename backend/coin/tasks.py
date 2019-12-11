import requests
from redis import Redis

from coin.app import app


def launch_task(func, description, *args, **kwargs):
    rq_job = app.task_queue.enqueue_call(func=func, result_ttl=5000, args=args, kwargs=kwargs)
    print(rq_job)


def consensus_requests(*args, **kwargs):
    for peer in kwargs['peers']:
        requests.get(peer + '/node/consensus/')


def mine_and_consensus(peer: str):
    r = requests.get(peer + '/miner/mine/')
    print(r.status_code)


def mine():
    r: Redis = app.redis
    if not r.getset('is_mining', True):
        app.node.mine(app.wallet.identity, app.wallet.identity)
        r.set('is_mining', False)


def example(seconds):
    print('Starting task')
    import time
    for i in range(seconds):
        print(i)
        time.sleep(1)
    print('Task completed')
