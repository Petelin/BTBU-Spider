from redis import Redis

from cls import settings


class PasswordError(RuntimeError):
    pass


redis = Redis.from_url(settings.redis_url)


def incr(key, time=60):
    if not redis.exists(key):
        redis.set(key, 1, ex=time)
    else:
        redis.incr(key)


def over_limit(key):
    if not redis.exists(key) or int(redis.get(key)) < settings.fail_count_limit:
        return False
    return True


def get(key):
    return redis.get(key)


def get_ip(request):
    if request.remote_addr != '127.0.0.1':
        ip = request.remote_addr
    else:
        ip = request.headers.get('X-Real-IP', None) or \
             request.headers.get('X-Forwarded-For', None)
    return ip

pp_redis = Redis.from_url(settings.pp_redis_url)


def get_proxy():
    name = pp_redis.randomkey()
    return pp_redis.hmget(name, ('ip', 'port')), name

def rm_proxy(name):
    if redis.exists(name):
        new_score = int(redis.get(name)) // 2
        if new_score==0:
            redis.delete(name)
            return {1:True, 0:False}[pp_redis.delete(name)]
        else:
            redis.set(name, new_score)
    else:
        return {1:True, 0:False}[pp_redis.delete(name)]

def good_proxy(name):
    if not redis.exists(name):
        redis.set(name, 2)
    else:
        redis.incr(name)
