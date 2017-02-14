from logging import Logger, FileHandler, Formatter, WARN, INFO, DEBUG

DEBUG = False

### logger config
logger = Logger('cls')
WARN_LOGGER = "/tmp/cls_warn.log"
INFO_LOGGER = "/tmp/cls_info.log"
DEBUG_LOGGER = "/tmp/cls_debug.log"
formatter = Formatter("%(asctime)s - %(levelname)s - %(message)s")

filewarnhandler = FileHandler(WARN_LOGGER, 'a')
filewarnhandler.setLevel(WARN)
filewarnhandler.setFormatter(formatter)

fileinfohandler = FileHandler(INFO_LOGGER, 'a')
fileinfohandler.setLevel(INFO)
fileinfohandler.setFormatter(formatter)

filedebughandler = FileHandler(DEBUG_LOGGER, 'a')
filedebughandler.setLevel(DEBUG)
filedebughandler.setFormatter(formatter)

logger.addHandler(filewarnhandler)
logger.addHandler(fileinfohandler)
logger.addHandler(filedebughandler)

# origin_warning = logger.warning
#
#
# def my_warning(*args, **kwargs):
#     origin_warning(locals())
#     return origin_warning(*args, **kwargs)
#
#
# logger.warning = my_warning

### redis
redis_url = 'redis://127.0.0.1:6379'
pp_redis_url = 'redis://127.0.0.1:6379/1'

fail_count_limit = 6

VPN_FAIL_KEY = 'cls.vpn.fail_count'

###

MIDDLEWARES = ["ProfileMiddleWare"]
