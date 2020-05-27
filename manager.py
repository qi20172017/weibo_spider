from account import Account
from token_ import Token
from interface import BackAccess
from setting import *
from action import Browser, Login, Home, Abnormal, Feedback
from task import TaskFollow, TaskHost, TaskForward
from log import Log
from tools import *
log = Log(__name__).get_log()


class Manager:
    def __init__(self):

        self.account = Account()
        self.token_ = Token().get_token()
        self.back_access = BackAccess()
        self.browser = Browser()
        self.my_browser = self.browser.get_browser()
        self.login = Login(self.my_browser)
        self.home = Home(self.my_browser)
        self.abnormal = Abnormal(self.my_browser)
        self.task_follow = TaskFollow(self.my_browser)
        self.task_host = TaskHost(self.my_browser)
        self.task_forward = TaskForward(self.my_browser)
        self.feed_back = Feedback(self.my_browser)
        # self.acc = ''
        # self.pwd = ''
        # self.id = ''

    def account_manager(self):
        code, data_, str = self.account.get_account(1)
        if code == 0:
            log.info("账号：{} 密码：{} ID：{}".format(data_[0]['acc'], data_[0]['pwd'], data_[0]['id']))
            return data_[0]['acc'], data_[0]['pwd'], data_[0]['id']
        else:
            return None, None, None

    def do_login(self, acc, pwd):
        if self.login.login(acc, pwd):
            if self.abnormal.is_into_verify():
                return 2
            if self.abnormal.is_into_recommend():
                return 1
            return 0
        else:
            if self.abnormal.is_into_inter_phone_num():
                return 4
            return 3

    def deal_abnormal_account(self):
        self.browser.close_browser()
        self.account.del_account(1)

    def deal_follow_failed(self):
        # self.browser.close_browser()
        # self.account.del_account(1)
        sleep_time(3)
        self.home.go_to_home()

    def deal_verify_page(self):
        self.browser.close_browser()
        self.account.del_account(1)

    def deal_login_failed(self):
        self.browser.close_browser()
        self.account.del_account(1)

    def deal_into_inter_phone_number(self):
        self.browser.close_browser()
        self.account.del_account(1)

    def update_follow(self, data):
        self.back_access.update_followed(token_=self.token_, data=data)

    def update_forward(self, data, id_):
        for item in data:
            item['RobotId'] = id_
            self.back_access.update_forward(token_=self.token_, action=item)

    @staticmethod
    def execute_cmd():
        os.system("ps -ef | grep chrom | grep -v grep | cut -c 9-15 | xargs kill -s 9")


    def manager(self):
        acc, pwd, id_ = self.account_manager()
        if acc:
            pass
        else:
            return
        login_res = self.do_login(acc, pwd)
        if login_res == 0:
            log.debug("登录状态0：登录成功！")
            pass
        elif login_res == 1:
            log.debug("登录状态1：进入推荐页！")
            pass
        elif login_res == 2:
            log.debug("登录状态2：进入验证页面！")
            self.deal_verify_page()
            return False
        elif login_res == 3:
            log.debug("登录状态3：登录失败！")
            self.deal_login_failed()
            return False
        elif login_res == 4:
            log.debug("登录状态4：进入了输入电话号码页面")
            self.deal_into_inter_phone_number()
        for i in range(3):
            sleep_time(3)
            follow_res, follow_data = self.task_follow.execute_follow(token_=self.token_, follower_id=id_)
            if follow_res == 0:
                log.debug("关注状态0：正常关注！")
                self.update_follow(data=follow_data)
                self.home.go_to_home()
            elif follow_res == 1:
                log.debug("关注状态1：账号异常！")
                self.deal_abnormal_account()
                return False
            elif follow_res == 2:
                log.debug("关注状态2：关注失败，只是暂时失败！")
                self.deal_follow_failed()
                continue
            elif follow_res == 3:
                log.debug("关注状态3：没有要关注的人！")
                pass
            sleep_time(9)
            forward_res = self.task_forward.execute_forward(token_=self.token_, robot_id=id_)
            if forward_res == 0:
                log.debug("转发状态0：转发成功！")
                self.home.go_to_home()
            elif forward_res == 1:
                log.debug("转发状态1：账号异常！")
                self.deal_abnormal_account()
                return False
            elif forward_res == 2:
                log.debug("转发状态2：没有关注的人，没有内容需要转发！")
                # 没有关注的人当然不转发
                # return
                pass
            sleep_time(9)
            feed_back_res = self.feed_back.get_self_forward()
            if feed_back_res:
                log.debug("获取转发内容：获取到数据！")
                self.update_forward(feed_back_res, id_)
            else:
                log.debug("获取转发内容：没有获取到数据！")
                pass
            sleep_time(9)
        self.browser.close_browser()
        return False


def run():
    try:
        my_manager = Manager()
        my_manager.manager()
        sleep_time(9)
    except:
        Manager.execute_cmd()


if __name__ == '__main__':
    run()


