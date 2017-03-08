def _is_sunder(key):
    return all((key.startswith('_'), key.endswith('_'), len(key) > 1))


def _is_dunder(key):
    return all((key.startswith('__'), key.endswith('__'), len(key) > 4))


class _EnumDict(dict):
    def __setitem__(self, key, value):
        if _is_sunder(key):
            # raise AttributeError('Cannot assign variable with _ start.')
            return
        if _is_dunder(key):
            return
        if not isinstance(value, (tuple, str, int, list)):
            return
        return super(_EnumDict, self).__setitem__(key, value)

    def __getitem__(self, item):
        return self[item]

    @classmethod
    def gen(cls, d):
        ins = cls()
        for k, v in d.items():
            ins[k] = v
        return ins


class EnumMeta(type):
    def __new__(cls, name, bases, dict):
        attrdict = _EnumDict.gen(dict)
        enum_class = super(EnumMeta, cls).__new__(cls, name, bases, dict)
        enum_class._value2object_ = {}
        enum_class._name2object_ = {}
        if bases != ():
            for variable_name, v in attrdict.items():
                delattr(enum_class, variable_name)
                if isinstance(v, tuple):
                    value = v[0]
                    desc = v[1]
                else:
                    value = v
                    desc = ''
                inst = enum_class(int(value), desc)
                # setattr(enum_class, variable_name, value)
                enum_class._name2object_[variable_name] = inst
                enum_class._value2object_[value] = inst
        return enum_class

    def __getattr__(cls, item):
        return cls._name2object_[item].code



class Enum(metaclass=EnumMeta):
    __slot__ = ['code', 'message']

    def __init__(self, code, message):
        assert isinstance(code, int)
        assert isinstance(message, str)
        self.code = code
        self.message = message

    @classmethod
    def getDesc(cls, code):
        for v, enum in cls._value2object_.items():
            if v == code:
                return enum.message
        return ''


class VPN_EXCEPTION(Enum):
    ERROR = (0, '错误')
    PASSWORD_ERROR = (100, '上网登陆密码错误')
    OVERLOAD = (101, '查询次数太多,学校vpn禁止了ip,没人的时候再来吧~~')


class JWC_EXCEPTION(Enum):
    ERROR = (0, '错误')
    PARAM_ERROR = (1, '参数错误')
    PASSWORD_ERROR = (100, '教务处登陆密码错误')
    UNKNOW_ERROR = (101, '教务处登陆密码错误')


class BaseException(Exception):
    def __init__(self, code, message=''):
        self.code = code
        self.message = message or VPN_EXCEPTION.getDesc(code) or JWC_EXCEPTION.getDesc(code)
        super(BaseException, self).__init__(self.code, self.message)

    def __repr__(self):
        return "(%s)%s" % (self.code, self.message)


if __name__ == '__main__':
    assert VPN_EXCEPTION.ERROR == 0
    print('done')