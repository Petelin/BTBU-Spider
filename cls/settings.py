from logging import Logger, FileHandler, Formatter, WARN, INFO

DEBUG = False

### logger config
logger = Logger('cls')
WARN_LOGGER = "/tmp/cls_warn.log"
INFO_LOGGER = "/tmp/cls_info.log"
formatter = Formatter("%(asctime)s - %(levelname)s - %(message)s")

filewarnhandler = FileHandler(WARN_LOGGER, 'a')
filewarnhandler.setLevel(WARN)
filewarnhandler.setFormatter(formatter)

fileinfohandler = FileHandler(INFO_LOGGER, 'a')
fileinfohandler.setLevel(INFO)
fileinfohandler.setFormatter(formatter)

logger.addHandler(filewarnhandler)
logger.addHandler(fileinfohandler)

### redis
redis_url = '127.0.0.1:6379'

fail_count_limit = 6

VPN_FAIL_KEY = 'cls.vpn.fail_count'

###

MIDDLEWARES = ["ProfileMiddleWare"]

