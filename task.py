from action import *
from interface import *
import random


class TaskFollow:
    def __init__(self, browser):
        self.browser = browser
        self.my_follow = Follow(self.browser)
        self.back_access = BackAccess()
        # self.token_ = token_
        # self.follower_id = follower_id
        self.abnormal = Abnormal(self.browser)
        self.data = None

    def __get_follow_page(self, token_, follower_id):
        code, data, msg = self.back_access.get_follow(token_=token_, follower_id=follower_id)
        follow_page = None
        if code == 0:
            self.data = data[0]
            follow_page = data[0]["FollowedHomepage"]
        return follow_page

    def execute_follow(self, token_, follower_id):
        follow_page = self.__get_follow_page(token_=token_, follower_id=follower_id)
        if follow_page:
            self.my_follow.follow(follow_page=follow_page)
            if self.abnormal.is_account_abnormal():
                return 1, None
            if self.abnormal.is_follow_failed():
                return 2, None
            return 0, self.data
        else:
            return 3, None


class TaskForward:
    def __init__(self, browser):
        self.browser = browser
        self.my_forward = Forward(self.browser)
        self.back_access = BackAccess()
        # self.token_ = token_
        # self.robot_id = robot_id
        self.abnormal = Abnormal(self.browser)

    def __get_followed(self, token_, robot_id):
        followed_list = self.back_access.get_followed(token_=token_, follower_id=robot_id)
        if followed_list:
            return random.choice(followed_list)
        else:
            return ''

    def __get_forward(self, token_, robot_id):
        forward_list = self.back_access.get_forward(token_=token_, robot_id=robot_id)
        return forward_list

    def execute_forward(self, token_, robot_id):
        """
        0:成功，1：账号异常， 2：没有要关注的人
        :return:
        """
        followed_page = self.__get_followed(token_, robot_id)
        forward_list = self.__get_forward(token_, robot_id)
        if followed_page:
            self.my_forward.into_new_page(followed_page)
            target_dict = self.my_forward.get_target()
            for item in target_dict:
                if item['post_id'] in forward_list:
                    continue
                else:
                    self.my_forward.into_new_page(item['url'])
                    self.my_forward.do_forward()
                    if self.abnormal.is_account_abnormal():
                        return 1
                    return 0
        else:
            return 2

# class TaskFeedBack:


class TaskHost:
    def __init__(self, browser):
        self.browser = browser
