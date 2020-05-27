import os
import time
from setting import *
from interface import BackAccess
from log import Log
from token_ import Token
from tools import get_host_ip
log = Log(__name__).get_log()


class Account:
    def __init__(self):
        self.__account_path = os.path.join(BASE_PATH, 'acc.prof')
        self.__account_number = 0
        self.__create_account_file()
        self.__back_access = BackAccess()

    def __account_file_existed(self):
        """
        判断文件是否存在
        :return:Bool
        """
        if os.path.exists(self.__account_path):
            return True
        else:
            return False

    def __create_empty_file(self):
        """
        创建一个空的文件
        :return:
        """
        with open(self.__account_path, 'w', encoding='utf-8')as f:
            f.write('')

    def __write_account_to_file(self, acc, pwd, id_):
        """
        将账号信息写入到文件
        :param acc: 账号
        :param pwd: 密码
        :param id_: id
        :return: None
        """
        data = acc + ' ' + pwd + ' ' + id_ + '\n'
        with open(self.__account_path, 'a', encoding='utf-8') as f:
            f.write(data)
        self.__account_number += 1

    def __read_account_from_file(self, order):
        """
        从文件中读取数据
        :return:元组（str, str, str）
        """
        with open(self.__account_path, 'r', encoding='utf-8') as f:
            data = f.readlines()
        acc, pwd, id_ = data[order-1].strip().split(' ')
        return acc, pwd, id_

    def __create_account_file(self):
        """
        创建账号文件 如果文件存在获取里面账号的数量
        :return:None
        """
        if self.__account_file_existed():
            self.__get_number_of_account()
        else:
            self.__create_empty_file()

    def __get_number_of_account(self):
        """
        获取文件中账号的数量
        :return: None
        """
        with open(self.__account_path, 'r', encoding='utf-8') as f:
            data = f.readlines()
        self.__account_number = len(data)

    def __get_new_account(self):
        """
        调用interface的借口，获取新的账号信息
        :return: 元组 （int, list, str）
        """
        token = Token().get_token()
        nick_name = get_host_ip()
        for i in range(10):
            code, data, msg = self.__back_access.get_robot_account(token_=token, platform=PLATFORM, nick=nick_name)
            if code == 0:
                return code, data, msg
            elif code == 1:
                time.sleep(5)
                continue
        return 1, [], '取了10次也没有取到'

    def __get_more_account(self):
        """
        获取一个账号，存入文件
        :return:Bool
        """
        code, data, msg = self.__get_new_account()
        if code == 0:
            acc = data[0]['acc']
            pwd = data[0]['pwd']
            id_ = data[0]['id']
            self.__write_account_to_file(acc, pwd, id_)
            return True
        elif code == 1:
            return False

    def __account_of(self, order):
        """
        返回第几个账号
        :param order:账号序号
        :return:元组（int, list, str）
        """
        if order > self.__account_number:
            if self.__get_more_account():
                acc, pwd, id_ = self.__read_account_from_file(order)
                log.debug('获取到新的账号')
                return 0, [{'acc': acc, 'pwd': pwd, 'id': id_}], ''
            else:
                log.debug('没有获取到账号')
                return 1, {}, '没有取到账号'
        else:
            acc, pwd, id_ = self.__read_account_from_file(order)
            log.debug('本地本来就有足够的账号')
            return 0, [{'acc': acc, 'pwd': pwd, 'id': id_}], ''

    def __del_account_of(self, order):
        """
        删除指定序号的账号信息
        :param order:
        :return:
        """
        with open(self.__account_path, 'r', encoding='utf-8') as f:
            data = f.readlines()
        acc, pwd, id_ = data[order-1].strip().split(' ')
        del data[order-1]
        with open(self.__account_path, 'w', encoding='utf-8') as f:
            f.writelines(data)
        self.__account_number -= 1
        log.info('删除成功,add: {}, pwd: {}, id: {}'.format(acc, pwd, id_))
        return 0, [{'acc': acc, 'pwd': pwd, 'id': id_}], '删除成功'

    def get_account(self, order):
        """
        外部调用的唯一借口
        :param order: 需要获取第几个账号
        :return:元组(int, list, str)
        """
        if order > SEVERAL_ACCOUNTS_PER_DEVICE or order <= 0:
            return 2, [], 'order数值不在范围内'
        else:
            return self.__account_of(order)

    def del_account(self, order):
        """
        从本地文件删除指定的账号
        :param order: 账号序号
        :return: 元组（int, list, str）
        """
        if order > SEVERAL_ACCOUNTS_PER_DEVICE or order <= 0:
            return 2, [], 'order数值不在范围内'
        elif order > self.__account_number:
            return 1, [], '没有那么多账户'
        else:
            return self.__del_account_of(order)


if __name__ == '__main__':
    account = Account()
    # code, data, msg = account.get_account(1)
    # print("code:{},data:{},msg:{}".format(code,data,msg))
    # data1 = account.get_account(1)
    # data2 = account.get_account(2)
    # data3 = account.get_account(3)
    # print(data1)
    # print(data2)
    # print(data3)
    res = account.del_account(2)
    print(res)
