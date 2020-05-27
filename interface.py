from setting import *
import requests
import json
import time
from log import Log
log = Log(__name__).get_log()


class BackAccess:

    def __post_data(self, sub_url, data):
        url = BASE_URL + sub_url
        log.debug("调用:{}, Post:{}".format(url, data))
        res = requests.post(url=url, json=data)
        log.debug("返回: {}, data: {}".format(url, res.text))
        try:
            data = json.loads(res.text)
            return data["RetCode"], data["Data"], data["Msg"]
        except:
            return 4, [{}], '数据格式错误，检查请求格式'

    def get_token(self):
        """
        {'RetCode': 0, 'Data': [{'Id': 9, 'Acc': 'crawler', 'Pwd': 'jysjcrawle', 'NickName': 'crawler', 'Typ': 11, 'Token': 'a779a11b8fc05d2118c830e1193a82c09ae61bfd8d8e6270f099fdbb5ebc1c8d'}], 'Msg': '', 'Total': 0}
        :return:
        """
        url = "acc/login"
        data = {"Acc": "crawler", "Pwd": "jysjcrawle"}
        code, data, msg = self.__post_data(sub_url=url, data=data)
        if code == 0:
            token_ = data[0]['Token']
            return 0, [{'token': token_}], ''
        else:
            return 1, [], '获取token失败'

    def get_robot_account(self, token_, platform, nick):
        """
        {'RetCode': 1, 'Data': None, 'Msg': '数据库错误', 'Total': 0}
        :param token_:
        :param platform:
        :param nick:
        :return:元组 （code, data, msg）
        """
        data = {"Data": {"token": token_, "platform": platform, "nick": nick}}
        url = "snsacc/GetAccToRun"
        code, data, msg = self.__post_data(url, data)
        if code == 0:
            acc = data[0]['Acc']
            pwd = data[0]['Pwd']
            id_ = data[0]['Id']
            log.info("机器人Acc: {}, Pwd: {}, Id: {}".format(acc, pwd, id_))
            return 0, [{'acc': acc, 'pwd': pwd, 'id': id_}], ''
        else:
            log.debug(msg)
            return 1, [], msg

    def get_chanel_name(self, token_, chanel_id):
        url = "robcommons/ListChanel"
        data = {"Data": {"token": token_}}
        succ, chanels, msg=self.__post_data(url, data)
        chanel_name = ""
        if chanels:
            for c in chanels:
                if c["Id"] == chanel_id:
                    chanel_name = c["Name"]
                    print("该账号的频道:", chanel_name)
        else:
            print("获取频道失败")

    def update_robot_status(self, token_, sns_acc, status):
        sns_acc["Status"]=status
        sns_acc["Token"]=token_
        # data = {"Data": {"token": token_, "Id": id_, "Status": status}}
        data = {"Items": [{"Token": token_, "Id": id_, "Status": status, "Typ": 2}], "Token": token_}
        url = "snsacc/UpdateStatus"
        code, data, msg = self.__post_data(url, data)
        print("code:{}".format(code))
        print("data:{}".format(data))
        print("msg:{}".format(msg))

    def insert_rob_acc(self, token_, acc, pwd, name, chanel_id, homepage, id_in_platform, platform_id=2, owner=1, typ=2):
        """
        插入账号信息
        :param token_: 令牌
        :param acc: 账号
        :param pwd: 密码
        :param name: 用户的昵称
        :param chanel_id: 频道
        :param homepage: 主页地址
        :param id_in_platform: 平台上的唯一ID
        :param platform_id: 平台ID
        :param owner: 1，是我们自己的号
        :param typ: 默认是2
        :return:
        """
        acc_info = {
            "Acc": acc,
            "ChanelId": chanel_id,
            "Homepage": homepage,
            "IdInPlatform": id_in_platform,
            "NickName": name,
            "Owner": owner,
            "PlatformId": platform_id,
            "Pwd": pwd,
            "Token": token_,
            "Typ": typ
        }
        data = {"Items": [acc_info], "Token": token_}
        url = "snsacc/upsert"
        code, data, msg = self.__post_data(url, data)
        if code == 0:
            log.info(msg)
        else:
            log.info(data)

    def get_follow(self, token_, follower_id):
        """
        发现这个接口无论有无数据，RetCode都为0，所以用data判断
        :param token_:
        :param follower_id:
        :return:
        """
        data = {"Data": {"token": token_, "follower": follower_id, "status": 1}}
        url = "snsacc/ListFollow"
        code, data, msg = self.__post_data(url, data)
        if data:
            log.debug(data)
            return 0, data, msg
        else:
            return 1, [{}], '没有更多需要关注的账户'
    # 有账号的时候
    # {'RetCode': 0, 'Data': [{'Id': '26782940268887428', 'Followed': '52203382485973491', 'FollowedHomepage': 'https://weibo.com/u/5970074811?refer_flag=1005050010_&is_hot=1', 'Follower': '39977743226676291', 'FollowerName': '花残_sfgbwq', 'FollowerIdInPlatform': '6890203356', 'Status': 1, 'CreatedAt': '', 'Token': ''}], 'Msg': '', 'Total': 0}
    # 没有账号的时候
    # {"RetCode":0,"Data":null,"Msg":"","Total":0}

    def get_followed(self, token_, follower_id):
        """
        获取已经关注的人的信息
        :param token_:
        :param follower_id:
        :return:list
        """
        data = {"Data": {"token": token_, "follower": follower_id, "status": 4}}
        url = "snsacc/ListFollow"
        code, data, msg = self.__post_data(url, data)
        res = []
        if data:
            log.debug(data)
            for item in data:
                home_page = item["FollowedHomepage"]
                res.append(home_page)
            # res是列表，里面是被关注者的主页链接
        return res

    def update_followed(self, token_, data):
        """
        把get_follow取到的data[0]数据数据放进来
        :param token_:
        :param data:
        :return:
        """
        url = "snsacc/UpdateFollow"
        data['Status'] = 4
        data['Token'] = token_
        code, data, msg = self.__post_data(url, data)
        log.info(msg)
        # {"RetCode":0,"Data":null,"Msg":"成功更新1行数据","Total":0}
        # 可以重复更新，更新成功就显示上面的结果，如果传入的参数有无会什么都不返回。

    def update_forward(self, token_, action):
        """
        action = {
        'ActionTyp':3 平台
        'RobotId':机器人账号
        'RobotName':sns_acc['NickName']
        'Comment':'值得转载的好文章',
        'ActionUrl':'https://weibo.com/6173171330/J22jNki7X?from=page_1005056173171320_profile&wvr=6&mod=weibotime&type=comment',
        'PlatformId':sns_acc['PlatformId'],
        'ClientAccId':'5970074811',
        'ClientPostUrl':'https://weibo.com/5970074811/IzOuwhXVT?from=page_1005055970074811_profile&wvr=6&mod=weibotime&type=comment#_rnd1589524161453',
        'ClientPostId':'IzOuwhXVT',
        'ClientPostTitle':'( ﹡ˆoˆ﹡ ) '
        }
        :param token_:
        :param action: 字典类型
        :return:
        """
        url = "snspostaction/upsert"
        data = {'Items': [action], 'Token': token_}
        code, data, msg = self.__post_data(url, data)
        log.info(msg)

    def get_forward(self, token_, robot_id):
        """
        查询已经转发的文章
        :param token_:
        :param robot_id:
        :return: list 有数据就放在列表中，没有数据就为空
        """
        url = "snspostaction/list"
        data = {"Data": {"token": token_, "robot_id": robot_id, "typ": 3}}
        # data = {'Items': [action], 'Token': token_}
        code, data, msg = self.__post_data(url, data)
        res = []
        if data:
            for item in data:
                if item["RobotId"] == robot_id:
                    res.append(item["ClientPostId"])
        # res 是列表里面放的已经转发的文章的id，['J2EJ0toC8']
        return res

    def save_v(self, token_, hot_user):
        """
        保存热门用户
        :param token_:
        :param hot_user:
        :return:None

        hot_user = {
        "IdInPlatform": '22222222',  str
        "NickName": 'hhhh',          str
        "PlatformId": int(2),        int
        "ChanelId": int(42),         int
        "Verified": False,           bool
        "VerifiedAs": '',            str
        "Homepage": 'www.baidu.com', str
        "Articals": int(0),          int
        "Videos": int(0),            int
        "Weibos": int(22),           int
        "Fans": int(22),             int
        "Follows": int(22)}          int
        """
        data = {"Token": token_, "Items": [hot_user]}
        url = "snsacc/upsert"
        succ, data, msg = self.__post_data(url, data)
        log.info(msg)


if __name__ == '__main__':
    my_back_access = BackAccess()
    code, token_, msg = my_back_access.get_token()
    if code == 0:
        token_ = token_[0]['token']
        print(token_)
    elif code == 1:
        print(msg)
    # id_ = '685106758792109'
    id_ = '65829792447702961'
    status = 3
    my_back_access.update_robot_status(token_=token_, id_=id_, status=status)
    # my_back_access.get_chanel_name(token_=token_, chanel_id=42)
    # code, data, msg = my_back_access.get_followed(token_=token_, follower_id='32226752729784943')
    # print(code)
    # print(data)
    # print(msg)

    # code, data, msg = my_back_access.get_forward(token_=token_, robot_id='38741991636331208')
    # print(msg)
    # if code == 0:
    #     i = 0
    #     for item in data:
    #         i+=1
    #         print(item)
    #     print(i)



    # code, data, msg = my_back_access.get_robot_account(token_=token, platform=2, nick='192.168.1.123')
    # if code == 0:
    #     print(data)
    # elif code == 1:
    #     print(msg)
    # acc='aaaaaaaaaa'
    # pwd='wwwww'
    # name='eeee'
    # chanelid=42
    # homepage='www.baidu.com'
    # idinplatform='fdsfs'
    # my_back_access.insert_rob_acc(token_=token_,acc=acc,pwd=pwd,name=name,chanel_id=chanelid,homepage=homepage,id_in_platform=idinplatform)


    # code, data, msg = my_back_access.get_followed(token_=token_, follower_id='519391188457681')
    # print('code: {}, data:{}, msg:{}'.format(code, data, msg))
    # data = {'Id': '26782940268887428', 'Followed': '52203382485973491', 'FollowedHomepage': 'https://weibo.com/u/5970074811?refer_flag=1005050010_&is_hot=1', 'Follower': '39977743226676291', 'FollowerName': '花残_sfgbwq', 'FollowerIdInPlatform': '6890203356', 'Status': 1, 'CreatedAt': '', 'Token': ''}
    # res = my_back_access.update_followed(token_=token_, data=data)
    # print('-----')
    # print('res:{}'.format(res))
    # action = {
    #     'ActionTyp':3,
    #     'RobotId': '519391188457681',
    #     'RobotName':'eeeee',
    #     'Comment':'值得转载的好文章',
    #     'ActionUrl':'https://weibo.com/6173171330/J22jNki7X?from=page_1005056173171320_profile&wvr=6&mod=weibotime&type=comment',
    #     'PlatformId':2,
    #     'ClientAccId':'5970074811',
    #     'ClientPostUrl':'https://weibo.com/5970074811/IzOuwhXVT?from=page_1005055970074811_profile&wvr=6&mod=weibotime&type=comment#_rnd1589524161453',
    #     'ClientPostId':'IzOuwhXVT',
    #     'ClientPostTitle':'( ﹡ˆoˆ﹡ ) '
    # }
    # my_back_access.update_forward(token_=token_,action=action)
    # hot_user = {
    #     "IdInPlatform": '22222222',
    #     "NickName": 'hhhh',
    #     "PlatformId": int(2),
    #     "ChanelId": int(42),
    #     "Verified": False,
    #     "VerifiedAs": '',
    #     "Homepage": 'www.baidu.com',
    #     "Articals": int(0),
    #     "Videos": int(0),
    #     "Weibos": int(22),
    #     "Fans": int(22),
    #     "Follows": int(22)}
    # my_back_access.save_v(token_=token_, hot_user=hot_user)
