from logging import Logger, FileHandler, Formatter, WARN, INFO

DEBUG = True

SECRET_KEY = "QNGRS$K53.4r1<XIcgCs2aj^x0yMEbY?m!tH(f9',~{TOhn8/dq;A=kU#PiF:}lu"

### logger config
logger = Logger('cls')
WARN_LOGGER = "E://cls_warn.log"
INFO_LOGGER = "E://cls_info.log"
DEBUG_LOGGER = "E://cls_debug.log"
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
###

MIDDLEWARES = ["ProfileMiddleWare"]
