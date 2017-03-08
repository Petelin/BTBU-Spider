# coding: utf-8
import os
from io import BytesIO

import requests
from PIL import Image


class BaseCode():
    # 验证码中，单个元素的图片名字
    BASEIDCODES = ["1", "2", "3", "b", "c", "m", "n", "v", "x", "z"]

    def __init__(self, absfilelocation):
        self.pixel_count = [[0] * 10 for x in range(12)]
        self.base_image = Image.open(absfilelocation)
        self.init_pixel_count()

    def init_pixel_count(self):
        for y in range(0, 12):
            for x in range(0, 9):
                self.pixel_count[y][x] = self.base_image.getpixel((x, y))

    def getpixel(self, x, y):
        return self.pixel_count[y][x]


class BaseCodeStore():
    pool = None

    @staticmethod
    def setup_basecode():
        path = os.path.dirname(__file__)
        BaseCodeStore.pool = {str(index): BaseCode(os.path.join(path, 'yzm', index) + '.bmp')
                              for index in
                              BaseCode.BASEIDCODES}

    @staticmethod
    def get_basecode(index):
        return BaseCodeStore.pool[index]


def get_idcode(img_url, **kwargs):
    """
        切图,和本地图片挨个像素对比,找出错误最少的.
    :param img_url: 验证码的路径
    :return:验证码字符串
    """
    response = requests.get(img_url, verify=False, **kwargs)
    content_file = BytesIO(response.content)
    content_file.seek(0)
    try:
        idcode_image = Image.open(content_file)
        id_code = ""
        # 切图识别验证码中的数字
        for qietu in range(0, 4):
            error_num_list = [12 * 10] * 10
            for i, base_code_index in enumerate(BaseCode.BASEIDCODES):
                error_pixel = 0
                for y in range(0, 12):
                    for x in range(0, 10):
                        now_pixel_count = sum(idcode_image.getpixel((x + 3 + 10 * qietu, y + 4)))
                        now_pixel_count = 0 if now_pixel_count > 700 else 255
                        base_pixel_count = BaseCodeStore.get_basecode(base_code_index).getpixel(x, y)
                        if now_pixel_count != base_pixel_count:
                            error_pixel += 1
                error_num_list[i] = error_pixel
                if error_pixel < 10:
                    break
            one_of_idcode = error_num_list.index(min(error_num_list))
            id_code += BaseCode.BASEIDCODES[one_of_idcode]
    finally:
        content_file.close()
    return id_code


if __name__ == "__main__":
    BaseCodeStore.setup_basecode()
    # for i in range(50):
    inner_url = "http://jwgl.btbu.edu.cn/verifycode.servlet"
    print(get_idcode(inner_url))
    from time import sleep
    sleep(6000000)
