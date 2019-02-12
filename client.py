# -*- coding: utf-8 -*-
# @File  : client.py
# @Author: WongHungching
# @Date  : 2019/1/26
# @Desc  : 网盘客户端

from pybdc import utils
from pybdc import settings
from pybdc import logger


class Client(object):

    def __init__(self, bd_cookie=None, bd_token=None):
        """
        bd_cookie：网盘web端cookie
        bd_token：手动对网盘web端操作，在请求参数中即可获得bdstoken
        """
        if bd_cookie is None:
            logger.debug("请输入百度cookie！")
        if bd_token is None:
            logger.debug("请输入百度token！")
        self.bd_cookie = bd_cookie
        self.bd_token = bd_token

        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Cookies": self.bd_cookie
        }

        # 插入工具：创建目录、上传文件、上传目录
        self.insert_utils = utils.InsertUtils(
            cookie=self.bd_cookie, token=self.bd_token)

        # 删除工具：删除目录、删除文件
        self.delete_utils = utils.DeleteUtils(
            cookie=self.bd_cookie, token=self.bd_token)

        # 查询工具：查询指定目录下的文件列表
        self.select_utils = utils.SelectUtils(
            cookie=self.bd_cookie, token=self.bd_token)
        
        # 更新工具：修改目录名、修改文件名
        self.update_utils = utils.UpdateUtils(
            cookie=self.bd_cookie, token=self.bd_token)

        # 保存工具：将pan链接资源保存到指定目录
        self.save_utils = utils.SaveUtils(
            cookie=self.bd_cookie, token=self.bd_token)
