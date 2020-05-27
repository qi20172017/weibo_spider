#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
import time
import os
from setting import *


class Log(object):

    def __init__(self, logger=None, log_cate='weibo'):
        """
        将日志文件存到当前工作目录下的Logs文件夹中
        :param logger:
        :param log_cate:
        """
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(LOG_LEVEL)

        # 定义handler的输出格式
        formatter = logging.Formatter(
            '[%(asctime)s] %(filename)s->%(funcName)s line:%(lineno)d [%(levelname)s]%(message)s')

        if FILE_LOG is True:
            # 创建一个handler，用于写入日志文件
            self.log_time = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
            log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Logs')
            if not os.path.exists(log_path):
                os.makedirs(log_path)
            self.log_name = os.path.join(log_path, log_cate + self.log_time + '.log')
            fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8')  # 这个是python3的
            # fh.setLevel(logging.WARNING)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            fh.close()

        if CMD_LOG is True:
            # 再创建一个handler，用于输出到控制台
            ch = logging.StreamHandler()
            # ch.setLevel(logging.WARNING)
            ch.setFormatter(formatter)
            # 给logger添加handler
            self.logger.addHandler(ch)
            ch.close()

        #  添加下面一句，在记录日志之后移除句柄
        # self.logger.removeHandler(ch)
        # self.logger.removeHandler(fh)
        # 关闭打开的文件

    def get_log(self):
        return self.logger
