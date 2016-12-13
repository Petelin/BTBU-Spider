class PasswordError(RuntimeError):
    pass


def get_ip(request):
    if request.remote_addr != '127.0.0.1':
        ip = request.remote_addr
    else:
        ip = request.headers.get('X-Real-IP', None) or \
             request.headers.get('X-Forwarded-For', None)
    return ip
