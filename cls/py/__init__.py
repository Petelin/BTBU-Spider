# coding: utf-8


from .idcode import *
from .vpn import *

if __name__ == '__main__':
    html = get_score('1302010635', '12346', 'petelin1120', time='2014-2015-1')
    print((parse_score(html))+"")

