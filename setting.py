"""
配置文件
"""
import os
import logging


PLATFORM = 2

WEIUSER = '13528740588'
WEIPWD = '3y0t2aed'

YINGUSER = 'jysj2020'
YINGPWD = 'jysj123456'
YINGCODE = 'fd38f7e92eb6a1c9d76012b40ca55384'

HOST = "rm-uf64kgb22y5l1nau3ko.mysql.rds.aliyuncs.com"
USER = "root"
PASSWORD = "Alidan01123382"
DATABASE = "wei_bo"
CHARSET = 'utf8'

BASE_URL = "http://116.228.183.198:8888/api/"
TEST_TOKEN = "3d5d2977930365c87182c53ee21409d8435ccec8843a68c7d39e8d3512352f5e"
ROBOTO_ACC_ID = "61433375991851693"
ROBOTO_ACC_OWNER = 1
weibo_typ = 2
video_typ = 1
artical_typ = 0
'''0新插入，1 正在发布，2.发布失败，3.发布成功'''
POST_STATUS_NEW = 0
POST_STATUS_PUBLISHING = 1
POST_STATUS_FAILED = 2
POST_STATUS_SUCC = 3

TOKEN_EXPIRES = 60*60*24*2
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

FORWARD_EXPIRES = 60*20

# 48个
CHANEL_ID = [2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52]


LOG_LEVEL = logging.DEBUG
HEADLESS = False
CMD_LOG = True
FILE_LOG = False

SEVERAL_ACCOUNTS_PER_DEVICE = 3
