import time
import os
import requests
import socket
import random

class TxtHandler:

    @staticmethod
    def read_lines(path):
        with open(path, 'r', encoding='utf-8')as f:
            res = f.readlines()
        return res

    @staticmethod
    def write_lines(path, line):
        line = line + '\n'
        with open(path, 'a', encoding='utf-8')as f:
            f.write(line)


class PathHandler:

    @staticmethod
    def dir_path():
        """
        Get current directory path
        :return: path
        """
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def join_path(filename):
        """
        Get current directory file path
        :param filename: target file
        :return: path
        """
        return os.path.join(PathHandler.dir_path(), filename)


class IpHandler:

    def get_proxy(self):
        ip_url = 'http://api.ip.data5u.com/dynamic/get.html?order=5b14a7c835defdba1877c544bebb7c28&sep=4'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36', }

        while True:
            response = requests.get(url=ip_url, headers=headers).text
            if 'too many requests' in response:
                time.sleep(0.5)
                continue
            else:
                prox = {'http': 'http://' + response.strip(' '),
                        }
                break
        return prox


def get_host_ip():
    """
    查询本机ip地址
    :return:
    """
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]
    finally:
        s.close()
    return ip


def sleep_time(level=1):
    """
    睡眠级别
    1：睡眠3~5秒
    2:8~12秒
    3:30~40秒
    :param level:
    :return: None
    """
    if level == 1:
        time.sleep(random.uniform(3, 5))
    elif level == 2:
        time.sleep(random.uniform(8, 12))
    elif level == 3:
        time.sleep(random.uniform(30, 40))
    elif level == 9:
        time.sleep(60*60*random.uniform(1, 2))


if __name__ == '__main__':
    # print(PathHandler.dir_path())
    # print(PathHandler.join_path('username_fir.txt'))
    # print(IpHandler.get_proxy())
    ip = get_host_ip()
    print(ip)