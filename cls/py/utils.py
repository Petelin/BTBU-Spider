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
