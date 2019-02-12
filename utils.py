# -*- coding: utf-8 -*-
# @File  : utils.py
# @Author: WongHungching
# @Date  : 2019/1/26
# @Desc  : 网盘操作核心代码


from pybdc import settings
import requests
import time
import json
from pybdc import logger
import os
import re


def log_request(operate, url, headers, params, data=None):
    """
    operate：操作类型
    url：请求链接
    headers：请求头
    params：请求参数
    data：表单数据
    """
    logger.debug('%s\n\t链接|%s\n\t请求头|%s\n\t参数|%s\n\t表单|%s\n\t' % (operate, url,
                                                                  headers, params, str(data)))


class InsertUtils(object):
    """
    百度网盘创建目录\上传文件
    """

    def __init__(self, cookie, token, clienttype=0):
        self.cookie = cookie
        self.token = token
        self.clienttype = clienttype

        self.headers = {
            "Cookie": self.cookie,
            "User-Agent": settings.USER_AGENT
        }

    def create_dir(self, bd_dir=None):
        """

        :param bd_dir:
        :return:
        """

        if bd_dir is None:
            logger.warn("请输入路径！")
            return

        url = "https://pan.baidu.com/api/create"

        params = {
            "a": "commit",
            "channel": "chunlei",
            "web": "1",
            "app_id": "250528",
            "bdstoken": self.token,
            "logid": "MTU0ODQ2NzUyODMzMjAuMjMxNjA1MzgwMTEzNzc0OTY=",
            "clienttype": self.clienttype,
        }

        data = {
            "path": bd_dir,
            "isdir": 1,
            "block_list": "[]"
        }

        try:
            resp = requests.post(
                url=url,
                params=params,
                headers=self.headers,
                data=data,
            )

            log_request('创建目录', resp.url, str(params),
                        str(self.headers), str(data))

            text = json.loads(resp.text)
            logger.debug("返回|%s" % str(text))
        except Exception as ex:
            logger.error(ex)

    def upload_file(self, local_file_path, bd_path, bd_uss):
        """
        :param local_file_path: 待上传的本地文件路径
        :param bd_path:网盘目录
        :param bd_uss：手动上传，可获取BDUSS参数
        :return:
        """
        bd_path = '/'.join([bd_path, local_file_path])
        url = "https://pan.baidu.com/api/precreate"

        data = {
            "path": bd_path,
            "target_path": "/".join(bd_path.split("/")[:-1]),
            "autoinit": 1,
            # todo：block_list参数的意义未测出，但订制似乎不影响功能
            "block_list": '["5910a591dd8fc18c32a8f3df4fdc1761"]',
            "local_mtime": int(time.time()),
        }

        params = {
            "channel": "chunlei",
            "web": "1",
            "app_id": "250528",
            "bdstoken": self.token,
            "logid": "MTU0ODQ2NzUyODMzMjAuMjMxNjA1MzgwMTEzNzc0OTY=",
            "clienttype": self.clienttype,
            "startLogTime": int(time.time() * 1000)
        }

        uploadid = None
        try:
            resp = requests.post(
                url=url,
                headers=self.headers,
                params=params,
                data=data,
            )

            log_request('上传文件预处理', resp.url, str(
                params), str(self.headers), str(data))

            uploadid = json.loads(resp.text)["uploadid"]
            logger.debug("返回|%s" % resp.content.decode("utf-8"))
            logger.debug("上传预处理|uploadid|%s" % uploadid)

        except Exception as ex:
            logger.error(ex)
            return

        url = "https://c3.pcs.baidu.com/rest/2.0/pcs/superfile2"
        params = {
            "method": "upload",
            "app_id": "250528",
            "channel": "chunlei",
            "clienttype": 0,
            "web": 1,
            "BDUSS": bd_uss,
            "logid": "MTU0ODQ5MDI1NjI4MjAuNjE3ODM5ODEwMTg2NDkxOQ==",
            "path": bd_path,
            "uploadid": uploadid,
            "uploadsign": 0,
            "partseq": 0
        }

        files = {
            'file': ('blob', open(local_file_path, 'rb'), 'application/octet-stream'),
        }

        try:
            resp = requests.post(
                url="https://c3.pcs.baidu.com/rest/2.0/pcs/superfile2",
                headers=self.headers,
                params=params,
                data=None,
                files=files,
            )

            log_request('上传文件预处理', resp.url, str(
                params), str(self.headers), str(data))
            logger.debug("返回|%s" % resp.content.decode("utf-8"))
        except Exception as ex:
            logger.debug(ex)
            return

        md5 = json.loads(resp.text)["md5"]
        x_bs_file_size = resp.headers["x-bs-file-size"]
        content_md5 = resp.headers["Content-MD5"]
        url = "https://pan.baidu.com/api/create"

        params = {
            "isdir": 0,
            "rtype": 1,
            "channel": "chunlei",
            "web": 1,
            "app_id": "250528",
            "bdstoken": self.token,
            "logid": "MTU0ODU2MTU4NjY2NDAuNDM0OTUwOTg1NTE5MzE5OQ==",
            "clienttype": 0,
        }

        data = {
            "path": bd_path,
            "size": str(x_bs_file_size),
            "uploadid": uploadid,
            "target_path": "/".join(bd_path.split("/")[:-1]),
            "block_list": '[\"' + content_md5 + '\"]',
            "local_mtime": int(time.time()),
        }
        try:
            resp = requests.post(
                url=url,
                headers=self.headers,
                params=params,
                data=data,
            )

            log_request('上传文件', resp.url, str(params),
                        str(self.headers), str(data))
            logger.debug("返回|%s" % resp.content.decode("utf-8"))
        except Exception as ex:
            logger.debug(ex)
            return

    def upload_dir(self, local_dir, bd_dir, bd_uss):
        """
        遍历文件夹下的文件，调用upload_file
        :param local_dir:本地目录
        :param bd_dir:网盘目录
        :param bd_uss：手动上传文件可获取BDUSS参数
        :return:
        """
        for item in os.walk(local_dir):
            file_dir = item[0]
            file_names = item[2]
            for item_ in file_names:
                file_path = file_dir + os.sep + item_
                logger.debug("本地路径|云盘路径\n\t%s  |  %s" %
                             (file_path, bd_dir))
                try:
                    self.upload_file(local_file_path=file_path,
                                     bd_path=bd_dir, bd_uss=bd_uss)
                except Exception as ex:
                    logger.debug(ex)
                    continue


class DeleteUtils(object):

    def __init__(self, cookie, token, clienttype=0):
        self.cookie = cookie
        self.token = token
        self.clienttype = clienttype

        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Cookie": self.cookie
        }

    def delete_dir(self, bd_dir):
        """
        :param bd_dir:
        :return:
        """
        self.delete_file(bd_dir)

    def delete_file(self, bd_file_path):
        """

        :param bd_file_path:
        :return:
        """
        url = "https://pan.baidu.com/api/filemanager"
        params = {
            "opera": "delete",
            "onnest": "fail",
            "async": 2,
            "channel": "chunlei",
            "web": "1",
            "app_id": "250528",
            "bdstoken": self.token,
            "logid": "MTU0ODQ2NzUyODMzMjAuMjMxNjA1MzgwMTEzNzc0OTY=",
            "clienttype": self.clienttype,
        }
        data = {
            "filelist": "[\"" + bd_file_path + "\"]"
        }

        try:
            resp = requests.post(
                url=url,
                params=params,
                headers=self.headers,
                data=data,
            )

            log_request('删除文件', resp.url, str(params),
                        str(self.headers), str(data))

            text = json.loads(resp.text)
            logger.debug("返回|%s" % str(text))
        except Exception as ex:
            logger.error(ex)


class UpdateUtils(object):

    def __init__(self, cookie, token, clienttype=0):
        self.cookie = cookie
        self.token = token
        self.clienttype = clienttype

        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Cookie": self.cookie
        }

    def modify_dir_name(self, bd_dir_old_path, bd_dir_new_name):
        """
        :param bd_dir_old_path:旧目录名
        :param bd_dir_new_path:新目录名
        :return:
        """
        self.modify_file_name(bd_dir_old_path, bd_dir_new_name)

    def modify_file_name(self, bd_file_old_path, bd_file_new_name):
        """

        :param bd_file_old_name:旧文件名，包括路径
        :param bd_file_new_name:新文件名，不包括路径
        :return:
        """

        url = "https://pan.baidu.com/api/filemanager"
        params = {
            "opera": "rename",
            "onnest": "fail",
            "async": 2,
            "channel": "chunlei",
            "web": "1",
            "app_id": "250528",
            "bdstoken": self.token,
            "logid": "MTU0ODQ2NzUyODMzMjAuMjMxNjA1MzgwMTEzNzc0OTY=",
            "clienttype": self.clienttype,
        }
        tmp = {
            "path": bd_file_old_path,
            "newname": bd_file_new_name
        }

        data = {
            "filelist": "[" + json.dumps(tmp) + "]"
        }

        try:
            resp = requests.post(
                url=url,
                params=params,
                headers=self.headers,
                data=data,
            )

            log_request('修改文件名', resp.url, str(
                params), str(self.headers), str(data))

            text = json.loads(resp.text)
            logger.debug("返回|%s" % str(text))
        except Exception as ex:
            logger.error(ex)


class SelectUtils(object):

    def __init__(self, cookie, token, clienttype=0):
        self.cookie = cookie
        self.token = token
        self.clienttype = clienttype

        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Cookie": self.cookie
        }


    def select_all_from_dir(self, bd_dir, num=100):
        """

        :param bd_dir:
        :return:
        """
        url = "https://pan.baidu.com/api/list"
        params = {
            "order": "time",
            "desc": 1,
            "showempty": 0,
            "page": 1,
            "num": num,
            "channel": "chunlei",
            "web": "1",
            "app_id": "250528",
            "bdstoken": self.token,
            "logid": "MTU0ODQ2NzUyODMzMjAuMjMxNjA1MzgwMTEzNzc0OTY=",
            "clienttype": self.clienttype,
            "startLogTime": str(time.time() * 1000),
            "dir": bd_dir,
            "t": "0.5",
        }
        data = None
        try:
            resp = requests.post(
                url=url,
                params=params,
                headers=self.headers,
            )

            log_request('查询文件列表', resp.url, str(
                params), str(self.headers), str(data))

            text = json.loads(resp.text)
            logger.debug("返回|%s" % str(text))
            return text
        except Exception as ex:
            logger.error(ex)


class SaveUtils(object):

    def __init__(self, cookie, token, clienttype=0):
        self.cookie = cookie
        self.token = token
        self.clienttype = clienttype

    def save_to_bd_dir(self, pan_url, pan_code=None, bd_dir="/"):
        """
        访问资源页面，不需要密码则提取fsidlist，shareid，from_，referer三个参数
        若需要密码，先输入密码，记录cookie，再提取参数
        不考虑图片验证码的情况
        :param pan_url:网盘链接
        :param pan_code:网盘密码
        :param bd_dir:百度云存储目录
        :return:
        """
        url = pan_url
        headers = {
            "User-Agent": settings.USER_AGENT,
            "Cookie": self.cookie,
            "Refefer": pan_url
        }

        if pan_code is not None:
            code_cookie = self.set_code_cookie(pan_url, pan_code)
            headers["Cookie"] = headers["Cookie"] + ";" + code_cookie

        params = None
        data = None
        try:
            resp = requests.post(
                url=url,
                params=params,
                headers=headers,
            )

            log_request('保存到网盘', resp.url, str(
                params), str(headers), str(data))
            text = resp.content.decode("utf-8")
            title = re.search("<title>(.*?)</title>", text).group(1)
            logger.debug("返回：%s" % title)
            if "密码" in title:
                # 输入密码错误或cookie无效
                logger.debug("密码cookie无效！")
                return
            else:
                # 提取数据
                file_data = re.search(
                    "yunData.setData\(({.*})\)", text).group(1)
                logger.debug("资源文件数据\n\t%s" % file_data)
                file_data = json.loads(file_data)
                # 提取三个核心参数
                shareid = file_data["shareid"]
                uk = file_data["uk"]
                fsidlist = file_data["file_list"]["list"]
                fsidlist = [str(item["fs_id"]) for item in fsidlist]
                logger.debug(fsidlist)

                # 上传
                try:
                    self.transfer_source(fsidlist=fsidlist, bd_dir=bd_dir, shareid=shareid, from_=uk, referer=pan_url,
                                         cookie=headers["Cookie"])
                except Exception as ex:
                    logger.error("上传失败")
                    logger.error(ex)
                    return

        except Exception as ex:
            logger.error(ex)

    def set_code_cookie(self, pan_url, pan_code):
        """
        输入密码返回cookie
        :param pan_url:
        :param pan_code:
        :return:
        """
        cookie = ""
        headers = {
            "User-Agent": settings.USER_AGENT,
            "Cookie": self.cookie,
            "Referer": pan_url

        }
        url = "https://pan.baidu.com/share/verify"
        surl = re.search("1([\w-]+)", pan_url).group(1)
        params = {
            "surl": surl,
            "t": str(int(time.time() * 1000)),
            "channel": "chunlei",
            "web": 1,
            "app_id": "250528",
            "bdstoken": self.token,
            "logid": "MTU0ODU4MzUxMTgwNjAuNDg5NDkyMzg5NzAyMzY1MQ==",
            "clienttype": self.clienttype
        }
        data = {
            "pwd": pan_code,
            "vcode": "",
            "vcode_str": ""
        }
        try:
            resp = requests.post(
                url=url,
                params=params,
                data=data,
                headers=headers,
            )

            log_request('保存资源|设置cookie', resp.url, str(
                params), str(headers), str(data))
            text = json.loads(resp.text)
            logger.debug("创建目录返回|%s" % str(text))

            cookie = resp.headers["Set-Cookie"]
            logger.debug("网盘密码cookie|%s" % cookie)
        except Exception as ex:
            logger.error(ex)
        return cookie

    def transfer_source(self, fsidlist, bd_dir, shareid, from_, referer, cookie=None):
        url = "https://pan.baidu.com/share/transfer"

        params = {
            "channel": "chunlei",
            "web": "1",
            "app_id": "250528",
            "bdstoken": self.token,
            "clienttype": self.clienttype,
            "logid": "MTU0ODQ2NzUyODMzMjAuMjMxNjA1MzgwMTEzNzc0OTY=",
            "shareid": shareid,
            "from": from_,
            "ondup": "newcopy",
            "async": 1,

        }

        fsidlist_str = "[" + ",".join(fsidlist) + "]"

        data = {
            "fsidlist": fsidlist_str,
            "path": bd_dir
        }

        headers = {
            "User-Agent": settings.USER_AGENT,
            "Cookie": cookie,
            "Referer": referer
        }

        try:
            resp = requests.post(
                url=url,
                params=params,
                headers=headers,
                data=data,
            )

            log_request('保存资源', resp.url, str(params),
                        str(headers), str(data))
            text = json.loads(resp.text)
            logger.debug("返回|%s" % str(text))
        except Exception as ex:
            logger.error(ex)
