"""
对微博的操作
"""
import time
import random
from chaojiying import Chaojiying_Client
from setting import *
from lxml import etree
import requests
import os
import re
# from dataAccess import BackgroundAccess
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from log import Log
from tools import sleep_time
import chaojiying
log = Log(__name__).get_log()


class Browser:
    def __init__(self):
        self.chaojiying = Chaojiying_Client(YINGUSER, YINGPWD, YINGCODE)
        self.options = Options()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        if HEADLESS is True:
            log.info("以无头模式启动浏览器")
            self.options.add_argument('--headless')
        self.__open_browser()

    def __open_browser(self):
        self.browser = webdriver.Chrome(chrome_options=self.options)
        self.browser.set_window_size(1800, 1000)
        sleep_time(1)
        self.browser.get('https://weibo.com/')
        sleep_time(1)
        log.info('打开浏览器，准备登陆')

    def get_browser(self):
        return self.browser

    def close_browser(self):
        self.browser.close()
        log.info('action：关闭浏览器')


class Login:
    def __init__(self, browser):
        self.browser = browser
        self.super_eagle = Chaojiying_Client(YINGUSER, YINGPWD, YINGCODE)
        self.login_abnormal = Abnormal(self.browser)
    def __inter_info(self, acc, pwd):
        sleep_time(1)
        log.info('输入用户名')
        self.browser.find_element_by_xpath(
            './/div[@class="W_login_form"]/div[contains(@class,"username")]//input').send_keys(acc)
        sleep_time(1)
        log.info('输入密码')
        self.browser.find_element_by_xpath(
            './/div[@class="W_login_form"]/div[contains(@class,"password")]//input').send_keys(pwd)

    def __clear_info(self):
        sleep_time(1)
        self.browser.find_element_by_xpath(
            './/div[@class="W_login_form"]/div[contains(@class,"username")]//input').clear()
        self.browser.find_element_by_xpath(
            './/div[@class="W_login_form"]/div[contains(@class,"password")]//input').clear()

    def __click_login(self):
        sleep_time(1)
        log.info('点击登录')
        self.browser.find_element_by_xpath(
            './/div[@class="login_innerwrap"]/div[3]/div[contains(@class,"login_btn")]').click()

    def __has_verify_code(self):
        sleep_time(1)
        html = etree.HTML(self.browser.page_source)
        res = html.xpath('.//div[@node-type="verifycode_box"]/@style')[0]
        if res == 'display: none;':
            log.info('没有验证码')
            return False
        else:
            log.info('有验证码')
            return True

    def __get_image(self, all_name, name):

        if os.path.exists(all_name):
            os.remove(all_name)
            log.info('删除原先的大图')
        if os.path.exists(name):
            os.remove(name)
            log.info('删除验证码图')
        canvas = self.browser.find_element_by_xpath('.//img[@node-type="verifycode_image"]')
        left = canvas.location['x']
        top = canvas.location['y']
        element_width = canvas.location['x'] + canvas.size['width']
        element_height = canvas.location['y'] + canvas.size['height']
        self.browser.save_screenshot(all_name)
        picture = Image.open(all_name)
        picture = picture.crop((left, top, element_width, element_height))
        picture.save(name)
        log.info('获取验证码成功，以保存本地')

    def __discern_code(self, code_img_path):
        im = open(code_img_path, 'rb').read()
        get_back = self.super_eagle.PostPic(im, 1005)['pic_str']
        log.info('获取到验证码：{}'.format(get_back))
        return get_back

    def __inter_code(self, verify_code):
        sleep_time(2)
        self.browser.find_element_by_xpath('.//input[@node-type="verifycode"]').send_keys(verify_code)

    def __clear_code(self):
        pass

    def __deal_with_code(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verifycode')
        code_img_path = os.path.join(path, 'code_img.png')
        code_img_path_all = os.path.join(path, 'all_code_img.png')
        self.__get_image(code_img_path_all, code_img_path)
        self.__inter_code(self.__discern_code(code_img_path))

    def __is_succeed(self):
        sleep_time(2)
        try:
            self.browser.find_element_by_xpath('.//div[@class="gn_nav"]/ul/li[5]')
            log.info('登录成功！')
            return True
        except:
            log.info('登录失败')
            return False

    def __to_login(self, acc, pwd):
        for i in range(10):
            self.__clear_info()
            self.__inter_info(acc, pwd)
            if self.__has_verify_code():
                self.__deal_with_code()
            self.__click_login()
            if self.__is_succeed():
                return True
            elif self.__has_verify_code():
                self.__deal_with_code()
                self.__click_login()
                if self.__is_succeed():
                    return True
            if self.login_abnormal.is_into_inter_phone_num():
                return False
            sleep_time(2)
        return False

    def login(self, acc, pwd):

        return self.__to_login(acc, pwd)


class Home:
    def __init__(self, browser):
        self.browser = browser

    def go_to_home(self):
        log.info('处理完关注，点击返回首页')
        self.browser.find_element_by_xpath('.//div[@class="gn_nav"]//li[1]//em[contains(@class,"S_txt1")]').click()


class Follow:

    def __init__(self, browser):
        self.browser = browser

    def __open_page(self, follow_page):
        sleep_time(1)
        self.browser.get(follow_page)
        log.info('打开被关注者主页：{}'.format(follow_page))

    def __is_followed(self):
        sleep_time(1)
        html = etree.HTML(self.browser.page_source)
        res = html.xpath('.//div[contains(@class,"opt_box")]/div[1]/a[1]/text()')[0]
        if res == '关注':
            log.info('未关注')
            return False
        elif res == '已关注':
            log.info('已关注')
            return True

    def __click_follow(self):
        sleep_time(2)
        self.browser.find_element_by_xpath('.//div[contains(@class,"opt_box")]/div[1]/a[1]').click()
        log.info('点击了关注')

    def follow(self, follow_page):
        """
        直接打开被关注的人的主页进行关注
        :param follow_page: 被关注人的主页链接
        :return:
        """
        sleep_time(2)
        self.__open_page(follow_page)
        if not self.__is_followed():
            self.__click_follow()


class Forward:

    def __init__(self, browser):
        self.browser = browser

    def __get_url(self):
        html = etree.HTML(self.browser.page_source)
        item_list = html.xpath('.//div[@node-type="feed_list"]//div[contains(@class,"WB_from")]/a[1]/@href')
        return item_list

    def get_target(self):
        item_list = self.__get_url()
        res = []
        for item in item_list:
            if re.findall(r'/\d+/\w+\?from', item):
                url = 'https://weibo.com' + item
                post_id = re.findall(r'/(\w+)\?from', item)[0]
                res.append({"url": url, "post_id": post_id})
        return res

    def into_new_page(self, url):
        sleep_time(2)
        self.browser.get(url)

    def __get_comment(self):
        """
        获取要评论的内容
        :return: str
        """
        html = etree.HTML(self.browser.page_source)
        detail_list = html.xpath('.//div[contains(@class,"WB_detail")]//div[contains(@class,"WB_text")]/text()')
        comment = random.choice(detail_list).strip()
        if len(comment) < 2:
            comment = '嗯嗯呐，转发一下吧'
        elif len(comment) > 80:
            comment = comment[:50]
        return comment

    def do_forward(self):
        sleep_time(2)
        comment = self.__get_comment()
        self.browser.find_element_by_xpath('.//div[contains(@class,"WB_feed_publish")]//textarea[@node-type]').send_keys(comment)
        sleep_time(1)
        self.browser.find_element_by_xpath('.//div[contains(@class,"WB_feed_publish")]//input[@id="ipt11"]').click()
        sleep_time(1)
        self.browser.find_element_by_xpath('.//div[contains(@class,"WB_feed_publish")]//a[contains(@class,"W_btn_a")]').click()
        sleep_time(1)


class Feedback:
    def __init__(self, browser):
        self.browser = browser

    def __into_main_page(self):
        sleep_time(1)
        self.browser.find_element_by_xpath('.//div[@class="gn_nav"]/ul/li[5]').click()
        log.info("进入个人主页，查看自己转发的微博内容")

    def get_self_forward(self):
        self.__into_main_page()
        sleep_time(2)
        res = []
        html = etree.HTML(self.browser.page_source)
        item_list = html.xpath('.//div[@node-type="feed_list"]//div[contains(@class,"WB_detail")]')
        if item_list:
            for item in item_list:
                try:
                    timestamp = item.xpath('./div[contains(@class,"WB_from")]/a[1]/@date')[0]
                    log.debug(timestamp)
                except:
                    timestamp = ''
                try:
                    action_url = 'https://weibo.com' + item.xpath('./div[contains(@class,"WB_from")]/a[1]/@href')[0]
                    log.debug(action_url)
                except:
                    action_url = ''
                try:
                    robot_name = item.xpath('./div[contains(@class,"WB_info")]/a/text()')[0]
                    log.debug(robot_name)
                except:
                    robot_name = ''
                try:
                    robot_comment_list = []
                    robot_comment_res = item.xpath('./div[contains(@class,"WB_text")]/text()')
                    for comment in robot_comment_res:
                        robot_comment_list.append(comment.strip())
                    robot_comment = ' '.join(robot_comment_list)
                    log.debug(robot_comment)
                except:
                    robot_comment = ''

                try:
                    client_acc_name = item.xpath('./div[contains(@class,"WB_feed_expand")]//div[contains(@class,"WB_info")]/a/@title')[0]
                    log.debug(client_acc_name)
                except:
                    client_acc_name = ''
                try:
                    client_title_list = []
                    client_title_res = item.xpath('./div[contains(@class,"WB_feed_expand")]//div[contains(@class,"WB_text")]/text()')
                    for title in client_title_res:
                        client_title_list.append(title.strip())
                    client_post_title = ' '.join(client_title_list)
                    log.debug(client_post_title)
                except:
                    client_post_title = ''
                try:
                    client_acc = item.xpath('./div[contains(@class,"WB_feed_expand")]//div[contains(@class,"WB_func")]/div[contains(@class,"WB_from")]/a[1]/@href')[0]
                    client_acc_id, client_post_id = client_acc.split('/')[1:]
                    client_post_url = 'https://weibo.com' + client_acc
                    log.debug("客户ID: {} 文章ID: {}".format(client_acc_id, client_post_id))
                except:
                    client_acc_id = ''
                    client_post_id = ''
                    client_post_url = ''
                weibo_data = {
                              'ActionTyp': 3,
                              'RobotName': robot_name,
                              'Comment': robot_comment,
                              'ActionUrl': action_url,
                              'PlatformId': 2,
                              'ClientAccId': client_acc_id,
                              'ClientPostUrl': client_post_url,
                              'ClientPostId': client_post_id,
                              'ClientPostTitle': client_post_title,
                              }
                res.append(weibo_data)
        return res


class Host:
    def __init__(self, browser):
        self.browser = browser

    def into_host(self):
        sleep_time(2)
        self.browser.find_element_by_xpath('.//div[@class="lev"]/a[@page_id="102803_ctg1_1760_-_ctg1_1760"]//span[2]').click()
        log.info("点击进入热门")

    def select_chanel(self):
        pass


class Abnormal:

    def __init__(self, browser):
        self.browser = browser

    def is_into_inter_phone_num(self):
        url = self.browser.current_url
        if url == 'https://sass.weibo.com/unfreeze':
            return True
        else:
            return False

    def is_into_recommend(self):
        sleep_time(2)
        try:
            self.browser.find_element_by_xpath('/html/body/div/div[1]/div/div/div[2]/div[1]/a').click()
            log.info('进入了推荐页')
            return True
        except:
            log.info('没有进入推荐页')
            return False

    def is_into_verify(self):
        """
        判断是否进入了验证页面
        :return:
        """
        sleep_time(2)
        try:
            self.browser.find_element_by_xpath('.//div[contains(@class,"geetest_holder")]')
            log.warning('为了解除帐号异常，请点击按钮进行验证')
            return True
        except:
            log.info('账号正常，不需要验证身份')
            return False

    def is_account_abnormal(self):
        """
        判断页面是否弹出了‘你的帐号存在异常，暂时无法发博、发评论、加关注等，请先验证身份解除异常。(100003)’
        :return:
        """
        sleep_time(2)
        try:
            self.browser.find_element_by_xpath('.//div[contains(@class,"W_layer")]//div[contains(@class,"W_layer_btn")]/a[1]')
            log.warning('你的帐号存在异常，暂时无法发博、发评论、加关注等，请先验证身份解除异常。(100003)')
            return True
        except:
            log.info('账号正常')
            return False

    def is_follow_failed(self):
        """
        判断是否出现'抱歉，关注失败(>_<) ，稍后再试啦。'的弹窗，这个弹窗说明还没有把本机养成常用设备。
        :return:
        """
        sleep_time(2)
        try:
            self.browser.find_element_by_xpath('.//div[contains(@class,"W_layer")]/div[contains(@class,"content")]/div[contains(@class,"W_layer_btn")]/a').click()
            log.warning('抱歉，关注失败(>_<) ，稍后再试啦。')
            return True
        except:
            log.info('没有出现关注失败')
            return False

    def is_forbid_comment(self):
        pass



class Action:

    def login(self, username, password):
        """
        用户登录操作
        :param username: 用户名
        :param password: 用户密码
        :return: None
        """
        for i in range(10):
            self.sleep_time(2)
            log.info('输入用户名')
            self.browser.find_element_by_xpath(
                './/div[@class="W_login_form"]/div[contains(@class,"username")]//input').send_keys(username)
            self.sleep_time(1)
            log.info('输入密码')
            self.browser.find_element_by_xpath(
                './/div[@class="W_login_form"]/div[contains(@class,"password")]//input').send_keys(password)
            self.sleep_time(1)

            html = etree.HTML(self.browser.page_source)
            res = html.xpath('.//div[@node-type="verifycode_box"]/@style')[0]
            if res == 'display: none;':
                log.info('没有验证码 直接点击登录')
            else:
                log.info('有验证码 处理验证码')
                self.sleep_time(1)
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verifycode')
                code_img_path = os.path.join(path, 'code_img.png')
                code_img_path_all = os.path.join(path, 'all_code_img.png')
                if self.get_image(code_img_path_all, code_img_path):
                    self.sleep_time(1)
                    im = open(code_img_path, 'rb').read()
                    get_back = self.chaojiying.PostPic(im, 1005)['pic_str']
                    log.info(get_back)
                    self.browser.find_element_by_xpath('.//input[@node-type="verifycode"]').send_keys(get_back)
            self.sleep_time(1)

            log.info('点击登录')
            self.browser.find_element_by_xpath(
                './/div[@class="login_innerwrap"]/div[3]/div[contains(@class,"login_btn")]').click()
            self.sleep_time(1)
            log.info("查看是否点击登录后又出现了验证码")
            try:
                html = etree.HTML(self.browser.page_source)
                res = html.xpath('.//div[@node-type="verifycode_box"]/@style')[0]
                if res == 'display: none;':
                    log.info('没有验证码')
                else:
                    log.info('有验证码')
                    self.sleep_time(1)
                    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verifycode')
                    code_img_path = os.path.join(path, 'code_img.png')
                    code_img_path_all = os.path.join(path, 'all_code_img.png')
                    if self.get_image(code_img_path_all, code_img_path):
                        self.sleep_time(1)
                        im = open(code_img_path, 'rb').read()
                        get_back = self.chaojiying.PostPic(im, 1005)['pic_str']
                        log.info(get_back)
                        self.browser.find_element_by_xpath('.//input[@node-type="verifycode"]').send_keys(get_back)
                self.sleep_time(1)

                # 点击登录
                log.info('点击登录')
                self.browser.find_element_by_xpath(
                    './/div[@class="login_innerwrap"]/div[3]/div[contains(@class,"login_btn")]').click()
                self.sleep_time(1)
            except:
                log.info('没有出现点击登录后才出现验证码的情况')
            self.sleep_time(1)

            try:
                self.browser.find_element_by_xpath('/html/body/div/div[1]/div/div/div[2]/div[1]/a').click()
            except:
                log.info('没有进入推荐页')
            self.sleep_time(2)
            # 检查个人昵称框 以判断是否登录成功
            try:
                self.browser.find_element_by_xpath('.//div[@class="gn_nav"]/ul/li[5]')
                log.info('登录成功！')
                self.sleep_time(1)
                if self.into_verify():
                    return
                log.info('点击首页')
                self.browser.find_element_by_xpath(
                    './/div[@class="gn_nav"]//li[1]//em[contains(@class,"S_txt1")]').click()
                break
            except:
                # 清除输入框
                self.browser.find_element_by_xpath(
                    './/div[@class="W_login_form"]/div[contains(@class,"username")]//input').clear()
                self.browser.find_element_by_xpath(
                    './/div[@class="W_login_form"]/div[contains(@class,"password")]//input').clear()
                log.info('没有成功，再试一次！')

    def into_verify(self):
        """
        判断是否进入了验证页面
        :return:
        """
        try:
            self.browser.find_element_by_xpath('.//div[contains(@class,"geetest_holder")]')
            log.warning('为了解除帐号异常，请点击按钮进行验证')
            return True
        except:
            log.info('账号正常，不需要验证身份')
            return False

    def abnormal(self):
        """
        判断页面是否弹出了‘你的帐号存在异常，暂时无法发博、发评论、加关注等，请先验证身份解除异常。(100003)’
        :return:
        """
        try:
            self.browser.find_element_by_xpath('.//div[contains(@class,"W_layer")]//div[contains(@class,"W_layer_btn")]/a[1]')
            log.warning('你的帐号存在异常，暂时无法发博、发评论、加关注等，请先验证身份解除异常。(100003)')
            return True
        except:
            log.info('账号正常')
            return False

    def follow_failed(self):
        """
        判断是否出现'抱歉，关注失败(>_<) ，稍后再试啦。'的弹窗，这个弹窗说明还没有把本机养成常用设备。
        :return:
        """
        try:
            self.browser.find_element_by_xpath('.//div[contains(@class,"W_layer")]/div[contains(@class,"content")]/div[contains(@class,"W_layer_btn")]')
            log.warning('抱歉，关注失败(>_<) ，稍后再试啦。')
            return True
        except:
            log.info('没有出现关注失败')
            return False


    def get_myself_info(self):
        """
        登陆成功后，获取个人的微博昵称，微博id，微博主页的地址
        :return:
        """
        if self.verify_title('请先验证身份'):
            log.info('点击首页')
            self.browser.find_element_by_xpath('.//div[@class="gn_nav"]//li[1]//em[contains(@class,"S_txt1")]').click()
        self.sleep_time(1)
        html = etree.HTML(self.browser.page_source)
        try:
            nickname = html.xpath('.//div[contains(@class,"nameBox")]/a[1]/@title')[0]
        except:
            nickname = None
        try:
            href = html.xpath('.//div[contains(@class,"nameBox")]/a[1]/@href')[0]
            platform_id = href.split('/')[1]
        except:
            platform_id = None
        home_page = self.browser.current_url

        log.info('nick:%s, platform_id:%s, home_page:%s' % (nickname, platform_id, home_page))
        return nickname + ' ' + platform_id + ' ' + home_page

    def follow(self, followed_page):
        """
        直接打开被关注的人的主页进行关注
        :param followed_page: 被关注人的主页链接
        :return:
        """
        self.browser.get(followed_page)
        self.sleep_time(1)
        html = etree.HTML(self.browser.page_source)
        res = html.xpath('.//div[contains(@class,"opt_box")]/div[1]/a[1]/text()')[0]
        if res == '关注':
            self.browser.find_element_by_xpath('.//div[contains(@class,"opt_box")]/div[1]/a[1]').click()
            log.info('点击了关注')
            self.sleep_time(1)
            if self.abnormal():
                return False
            self.sleep_time(1)
        elif res == '已关注':
            log.info('已关注')
        self.sleep_time(1)
        log.info('处理完关注，点击返回首页')
        self.browser.find_element_by_xpath('.//div[@class="gn_nav"]//li[1]//em[contains(@class,"S_txt1")]').click()
        return True

    def crawl_V(self, chanels):
        """
        进入热门微博，根据热门微博分类去有条件的爬取用户信息
        :return:
        """
        stop = 0
        chanel_num = None
        self.sleep_time(1)
        # 点击入门微博
        self.browser.find_element_by_xpath('.//div[@class="lev"]/a[@page_id="102803_ctg1_1760_-_ctg1_1760"]//span[2]').click()
        self.sleep_time(1)
        # 获取热门微博的页面源码
        html = etree.HTML(self.browser.page_source)
        res = html.xpath('.//div[@id="Pl_Discover_TextList__4"]//ul[contains(@class,"ul_text")]/li//span/text()')
        # 找出目标频道
        for item in list(enumerate(res)):
            if item[1].strip() == chanels:
                chanel_num = item[0] + 1
                break
        if chanel_num:
            # 点击相应频道
            xpath_str = './/div[@id="Pl_Discover_TextList__4"]//ul[contains(@class,"ul_text")]/li[{}]//span'.format(chanel_num)
            self.browser.find_element_by_xpath(xpath_str).click()
            # 爬取100页的数据
            for j in range(2):
                # 每一页有90个，分6批，一批15个，所以需要下拉5次，加载这一整个页面
                print('这是第{}页'.format(j))
                self.sleep_time(1)
                self.slide_to()
                self.sleep_time(1)
                self.slide_to()
                self.sleep_time(1)
                self.slide_to()
                self.sleep_time(1)
                self.slide_to()
                self.sleep_time(1)
                self.slide_to()
                self.sleep_time(2)
                item_count = len(etree.HTML(self.browser.page_source).xpath('.//div[@node-type="feed_list"]/div[@action-type="feed_list_item"]'))
                start = 1 + stop
                stop = item_count
                print(start,stop)
                for i in range(start, stop):
                    # 构造头像的xpath语句
                    self.close_net_busy()
                    # 在点击到头像上之前，先滑动一下
                    # self.slide_to(i)
                    photo_xpath = './/div[@node-type="feed_list"]/div[{}]/div/div[contains(@class,"WB_face")]'.format(i)
                    # 找到元素，并将鼠标移动到元素上
                    photo = self.browser.find_element_by_xpath(photo_xpath)
                    ActionChains(self.browser).move_to_element(photo).perform()
                    self.sleep_time(2)
                    # 获取加载后的源码，提取粉丝数
                    try:
                        html = etree.HTML(self.browser.page_source)
                        fans = html.xpath('.//div[contains(@class,"W_layer_pop")]//div[@class="c_count"]/span[2]//em/text()')[0]
                        if fans[-1:] == '万':
                            fans = fans[:-1] + '0000'
                    except:
                        print('没有抓到粉丝数')
                        fans = '0'
                    else:
                        # 判断分数是否大于一万
                        if len(fans) > 4:
                            self.close_net_busy()
                            try:
                                follows = html.xpath('.//div[contains(@class,"W_layer_pop")]//div[@class="c_count"]/span[1]//em/text()')[0]
                            except:
                                follows = 0

                            try:
                                weibos = html.xpath(
                                    './/div[contains(@class,"W_layer_pop")]//div[@class="c_count"]/span[3]//em/text()')[
                                    0]
                            except:
                                weibos = 0
                            try:
                                id_in_platform_list = html.xpath('.//div[contains(@class,"W_layer_pop")]//div[@node-type="followBtnBox"]/@action-data')
                                id_in_platform = re.findall('uid=(\d+)&fnick', id_in_platform_list[0])[0]
                            except:
                                id_in_platform = ''
                            try:
                                verified_as = \
                                    html.xpath('.//div[contains(@class,"W_layer_pop")]//div[@class="pic_box"]/a[2]/i/@title')[0]
                                verified = True
                            except:
                                verified_as = ''
                                verified = False
                            try:
                                nickname = html.xpath('.//div[contains(@class,"W_layer_pop")]//div[@class="pic_box"]/a[1]/img/@title')[0]
                            except:
                                nickname = ''
                            try:
                                homepage = html.xpath('.//div[contains(@class,"W_layer_pop")]//div[@class="pic_box"]/a[1]/@href')[0]
                            except:
                                homepage = ''
                            self.bgaccess.save_V(id_in_platform, nickname, 2, 2, verified, verified_as, homepage, 0, 0,
                                                 weibos, fans, follows)
                        else:
                            print('粉丝数太少')
                self.crawl_hot(self.browser.page_source, start)
                # 如果需要加载更多，则点击

                for i in range(5):
                    try:
                        self.close_net_busy()
                        self.browser.find_element_by_xpath('.//span[contains(@class,"more_txt")]').click()
                        self.sleep_time(1)
                        print('点击查看更多')
                        break
                    except Exception as e:
                        print(e)
                        print('点击更多失败,再试一次')
                        self.sleep_time(1)
                else:
                    break

        else:
            print('没有这个频道')
            print('点击返回主页')
            self.browser.find_element_by_xpath('.//div[@class="gn_nav"]//li[1]//em[contains(@class,"S_txt1")]').click()
            self.sleep_time(1)

    def crawl_hot(self, page, start):
        html = etree.HTML(page)
        hot_item = html.xpath('.//div[@node-type="feed_list"]/div[@action-type="feed_list_item"]')
        for item in hot_item[start-1:]:
            # item_html = etree.HTML(item)
            item_html = item
            try:
                nick_name = item_html.xpath('./div[@node-type="feed_content"]//div[contains(@class,"WB_info")]/a/@nick-name')[0]
            except:
                nick_name = ''
            try:
                detail_url = item_html.xpath('./div[@node-type="feed_content"]//div[contains(@class,"WB_from")]/a[1]/@href')[0]
            except:
                detail_url = ''
            try:
                id_in_platform_list = item_html.xpath('./div[@node-type="feed_content"]//div[contains(@class,"WB_info")]/a/@usercard')
                id_in_platform = id_in_platform_list[0].split('&')[0].split('=')[1]
            except:
                id_in_platform = ''
            try:
                body_list = item_html.xpath('./div[@node-type="feed_content"]//div[contains(@class,"WB_text")]/text()')
                body = ''
                for item in body_list:
                    body += item.strip()
                body_res = re.findall('[\u4e00-\u9fa5\u0020-\u0080]', body)
                body = ''.join(body_res)
            except:
                body = ''
            try:
                body_sub_list = item_html.xpath('./div[@node-type="feed_content"]//div[contains(@class,"WB_text")]/a/text()')
                body_sub = ''
                for item in body_sub_list:
                    body_sub += item.strip()
                body_sub_res = re.findall('[\u4e00-\u9fa5\u0020-\u0080]', body_sub)
                body_sub = ''.join(body_sub_res)
            except:
                body_sub = ''
            body = body + body_sub

            try:
                video_src = item_html.xpath('./div[@node-type="feed_content"]//div[contains(@class,"media_box")]//li[contains(@class,"WB_video")]/div[1]/img/@src')[0]
            except:
                video_src = ''

            try:
                img_src_list = item_html.xpath('./div[@node-type="feed_content"]//div[contains(@class,"media_box")]//li/img/@src')
                img_src = ';'.join(img_src_list)
            except:
                img_src = ''
            try:
                vote_src_list = item_html.xpath('./div[@node-type="feed_content"]//div[contains(@class,"WB_media_wrap")]//div[contains(@class,"header")]//img/@src')
                vote_src = ';'.join(vote_src_list)
            except:
                vote_src = ''
            srcs = video_src + img_src + vote_src
            try:
                forwards = item_html.xpath('./div[@class="WB_feed_handle"]//li[2]//em[2]/text()')[0].strip()
            except:
                forwards = 0
            try:
                comments = item_html.xpath('./div[@class="WB_feed_handle"]//li[3]//em[2]/text()')[0].strip()
            except:
                comments = 0
            try:
                likes = item_html.xpath('./div[@class="WB_feed_handle"]//li[4]//em[2]/text()')[0].strip()
            except:
                likes = 0
            print(nick_name, detail_url, id_in_platform, body, srcs, forwards, comments, likes)

    def slide_to(self):
        """
        互动到底部
        :return:
        """
        # self.sleep_time(1)
        # location = 400*number
        js = "window.scrollTo(0, document.body.scrollHeight);"
        self.browser.execute_script(js)
        print('滑动一下')
        self.sleep_time(1)

    def close_net_busy(self):
        try:
            self.browser.find_element_by_xpath('.//div[contains(@class,W_translateZ)]//div[@class="W_layer_close"]/a').click()
            print('关闭了网络繁忙')
        except:
            print('正常进行')

    def verify_title(self, title):
        if title == self.browser.title:
            return True
        else:
            return False

    def sns_action_forward(self):
        """
        :return:
        """
        html = etree.HTML(self.browser.page_source)
        item_list = html.xpath('.//div[@node-type="feed_list"]//div[contains(@class,"WB_from")]/a[1]/@href')
        if item_list:
            pass
        else:
            self.browser.find_element_by_xpath('.//div[contains(@class,"WB_tab_a")]//ul/li[3]').click()
            self.sleep_time(1)
            html = etree.HTML(self.browser.page_source)
            item_list = html.xpath('.//div[@node-type="feed_list"]//div[contains(@class,"WB_from")]/a[1]/@href')

        for item in item_list:
            item = 'https://weibo.com' + item
            if re.findall(r'/\d+/\w+\?ref', item):
                self.browser.get(item)
                self.sleep_time(2)
                html = etree.HTML(self.browser.page_source)
                post_name = html.xpath('.//div[@node-type="feed_list"]//div[contains(@class,"WB_detail")]/div[contains(@class,"WB_info")]/a/text()')[0]
                my_name = html.xpath('.//div[@class="gn_nav"]/ul/li[5]/a/em[2]/text()')[0]
                if post_name != my_name:
                    try:
                        detail_list = html.xpath('.//div[contains(@class,"WB_detail")]//div[contains(@class,"WB_text")]/text()')
                        comment = random.choice(detail_list).strip()
                        if len(comment) < 2:
                            comment = '嗯嗯呐，转发一下吧'
                        elif len(comment) > 80:
                            comment = comment[:50]
                        self.browser.find_element_by_xpath('.//div[contains(@class,"WB_feed_publish")]//textarea[@node-type]').send_keys(comment)
                        self.sleep_time(1)
                        self.browser.find_element_by_xpath('.//div[contains(@class,"WB_feed_publish")]//input[@id="ipt11"]').click()
                        self.sleep_time(1)
                        self.browser.find_element_by_xpath('.//div[contains(@class,"WB_feed_publish")]//a[contains(@class,"W_btn_a")]').click()
                        self.sleep_time(1)
                        if self.abnormal():
                            return
                        else:
                            log.info("转发成功")
                    except:
                        log.info('禁止评论:%s' % item)
                else:
                    log.info('自己发表的不转发%s' % item)
            else:
                log.info('广告或者该链接已经被转发%s' % item)
            self.sleep_time(1)
        log.info('查看是否需要转发，处理完毕，点击返回主页')
        self.browser.find_element_by_xpath('.//div[@class="gn_nav"]//li[1]//em[contains(@class,"S_txt1")]').click()
        self.sleep_time(2)

    def get_my_weibo(self):
        """
        :return:
        """
        result_list = []
        self.sleep_time(1)
        self.browser.find_element_by_xpath('.//div[@class="gn_nav"]/ul/li[5]').click()
        log.info("进入个人主页，查看自己转发的微博内容")
        self.sleep_time(1)
        html = etree.HTML(self.browser.page_source)
        item_list = html.xpath('.//div[@node-type="feed_list"]//div[contains(@class,"WB_detail")]')
        if item_list:
            for item in item_list:
                try:
                    timestamp = item.xpath('./div[contains(@class,"WB_from")]/a[1]/@date')[0]
                    log.debug(timestamp)
                except:
                    timestamp = ''
                try:
                    action_url = 'https://weibo.com' + item.xpath('./div[contains(@class,"WB_from")]/a[1]/@href')[0]
                    log.debug(action_url)
                except:
                    action_url = ''
                try:
                    robot_name = item.xpath('./div[contains(@class,"WB_info")]/a/text()')[0]
                    log.debug(robot_name)
                except:
                    robot_name = ''
                try:
                    robot_comment_list = []
                    robot_comment_res = item.xpath('./div[contains(@class,"WB_text")]/text()')
                    for comment in robot_comment_res:
                        robot_comment_list.append(comment.strip())
                    robot_comment = ' '.join(robot_comment_list)
                    log.debug(robot_comment)
                except:
                    robot_comment = ''

                try:
                    client_acc_name = item.xpath('./div[contains(@class,"WB_feed_expand")]//div[contains(@class,"WB_info")]/a/@title')[0]
                    log.debug(client_acc_name)
                except:
                    client_acc_name = ''
                try:
                    client_title_list = []
                    client_title_res = item.xpath('./div[contains(@class,"WB_feed_expand")]//div[contains(@class,"WB_text")]/text()')
                    for title in client_title_res:
                        client_title_list.append(title.strip())
                    client_post_title = ' '.join(client_title_list)
                    log.debug(client_post_title)
                except:
                    client_post_title = ''
                try:
                    client_acc = item.xpath('./div[contains(@class,"WB_feed_expand")]//div[contains(@class,"WB_func")]/div[contains(@class,"WB_from")]/a[1]/@href')[0]
                    client_acc_id, client_post_id = client_acc.split('/')[1:]
                    client_post_url = 'https://weibo.com' + client_acc
                    log.debug(client_acc_id, client_post_id)
                except:
                    client_acc_id = ''
                    client_post_id = ''
                    client_post_url = ''
                log.debug('-' * 60)
                if int(time.time()*1000) - int(timestamp) < FORWARD_EXPIRES * 1000:
                    weibo_data = {'action_url':action_url,
                                  'robot_name':robot_name,
                                  'robot_comment':robot_comment,
                                  'client_acc_name':client_acc_name,
                                  'client_post_title':client_post_title,
                                  'client_acc_id':client_acc_id,
                                  'client_post_id':client_post_id,
                                  'client_port_url':client_post_url
                                  }
                    result_list.append(weibo_data)
        else:
            result_list = result_list
        log.info('点击返回主页')
        self.browser.find_element_by_xpath('.//div[@class="gn_nav"]//li[1]//em[contains(@class,"S_txt1")]').click()
        self.sleep_time(2)
        return result_list

if __name__ == '__main__':
    acc = 'ii2bhblh9z@sina.cn'
    pwd = '2A1B8E'
    my_bro = Browser().get_browser()
    if Login(my_bro).login(acc=acc, pwd=pwd):

        Abnormal.into_verify(my_bro)
