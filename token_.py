import os
import time
from setting import *
from interface import BackAccess
from log import Log
log = Log(__name__).get_log()


class Token:

    def __init__(self):
        self.__token_path = os.path.join(BASE_PATH, 'token.prof')
        self.__back_access = BackAccess()

    def __token_existed(self):
        if os.path.exists(self.__token_path):
            return True
        else:
            return False

    def __read_token_file(self):
        with open(self.__token_path, 'r', encoding='utf-8') as f:
            data = f.readline()
        return data

    def __write_token_file(self, token):
        with open(self.__token_path, 'w', encoding='utf-8') as f:
            f.write(token)

    def __get_new_token(self):
        code, data, msg = self.__back_access.get_token()
        if code == 0:
            token_ = data[0]['token']
            data = token_ + ' ' + str(int(time.time()))
            self.__write_token_file(data)
            log.info('新建的token')
            return token_
        elif code == 1:
            log.info(msg)
            return None

    def __get_old_token(self):
        data = self.__read_token_file()
        history_token, timestamp = data.split(' ')
        if int(time.time()) - int(timestamp) > TOKEN_EXPIRES:
            token = self.__get_new_token()
            log.info('过期了，刚取得token')
            return token
        log.info('历史的token')
        return history_token

    def get_token(self):
        if self.__token_existed():
            return self.__get_old_token()
        else:
            return self.__get_new_token()


if __name__ == '__main__':
    my_token = Token()
    print(my_token.get_token())

