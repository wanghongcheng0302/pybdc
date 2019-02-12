# -*- coding: utf-8 -*-
# @File  : __init__.py
# @Author: WongHungching
# @Date  : 2019/1/26
# @Desc  : 日志

import logging
from pybdc.settings import DEBUG, LOG_FILE

logger = logging.Logger("")
if DEBUG == True:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
file_headler = logging.FileHandler(filename=LOG_FILE, mode="w", encoding="utf-8")
file_headler.setFormatter(formatter)
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(file_headler)
logger.addHandler(console)

