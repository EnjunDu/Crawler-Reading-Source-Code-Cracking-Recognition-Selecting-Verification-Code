import time
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import random
import requests
from hashlib import md5
from bs4 import BeautifulSoup

class Chaojiying(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        self.password = md5(password.encode('utf-8')).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def post_pic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        return r.json()

    def report_error(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


# 日志输出配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


# 缩小图片
def shrink():
    code = Image.open("code.png")
    shrink_img = code.resize((169, 216))
    shrink_img.save("shrink_img.png")
    print(code.size, shrink_img.size)


# 提交给超级🦅识别
def check():
    USERNAME = '929231882'
    PASSPORT = 'skyzs12138.'
    SOFT_ID = '929231882'
    CAPTCHA_KIND = '9004'
    FILE_NAME = 'shrink_img.png'
    client = Chaojiying(USERNAME, PASSPORT, SOFT_ID)
    result = client.post_pic(open(FILE_NAME, 'rb').read(), CAPTCHA_KIND)
    # logging.info(result)
    return result


def parse_data(result):
    node_list = []
    locations = result['pic_str']
    print(result)
    if '|' in locations:
        nums = locations.split('|')
        for i in range(len(nums)):
            x = int(nums[i].split(',')[0])
            y = int(nums[i].split(',')[1])
            xy_list = [x, y]
            node_list.append(xy_list)
    else:
        print(locations.split(',')[0])
        print(locations.split(',')[1])
        x = int(locations.split(',')[0])
        y = int(locations.split(',')[1])
        xy_list = [x, y]
        node_list.append(xy_list)
    return node_list


def click_codeImg(all_list, code_img_ele):

    # 减去偏移从左上角开始
    x0 = code_img_ele.rect['width']/2
    y0 = code_img_ele.rect['height']/2
    for item in all_list:
        x = int(item[0] * 1.89)
        y = int(item[1] * 1.89)

        # 噫 好 好！ 调了一晚上的bug 噫 好！
        ActionChains(driver).move_to_element_with_offset(code_img_ele, x-x0 , y-y0).click().perform()
        time.sleep(random.random())
        logging.info('点击成功！')

    time.sleep(random.random()*2)
    driver.find_element(By.XPATH, '//a[@class="geetest_commit"]').click() # 点击后
    # driver.find_element(By.XPATH, '//div[text()="登录"]').click() # 点击前
    time.sleep(5)


def save_img():
    driver.find_element(By.XPATH, "//button").send_keys(Keys.ENTER)
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@class="geetest_widget"]')))
        # 获取验证码位置
        captcha_image = driver.find_element(By.XPATH, '//div[@class="geetest_widget"]')

        driver.save_screenshot('page.png')
        location = captcha_image.location
        size = captcha_image.size

        # 得到左上角和右下角的坐标
        rangle = (
            int(location['x'] * 1.25), int(location['y'] * 1.25), int((location['x'] + size['width']) * 1.25),
            int((location['y'] + size['height']) * 1.25)
        )
        image1 = Image.open('page.png')
        frame = image1.crop(rangle)
        frame.save('code.png')

        return captcha_image

    except TimeoutException:
        return save_img()

def main():
    code_img_ele = save_img()
    shrink()
    result = check()
    all_list1 = parse_data(result)
    click_codeImg(all_list1, code_img_ele)


while True:
    i=1
    # 启动！
    options = webdriver.ChromeOptions()
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ['enable-automation'])

    # 使用Google
    driver = webdriver.Chrome(options=options)

    driver.get("https://captcha3.scrape.center/")
    driver.maximize_window()

    # 找到用户名和密码输入框并输入信息
    username_input = driver.find_element(By.XPATH, "//input[@type='text']")
    password_input = driver.find_element(By.XPATH, "//input[@type='password']")
    username_input.send_keys("admin")
    password_input.send_keys("admin")

    # 找到登录按钮并点击                                                     js方案失败
    # js = 'document.getElementTagName("button").click()' # js点击元素
    # driver.execute_script(js)
    time.sleep(4)
    main()
    success_element = driver.page_source  # 获取点击按钮后页面的HTML
    if success_element:
        soup = BeautifulSoup(success_element, 'html.parser')
        success_text = soup.get_text()
        if i>1:
            print("上次测试失败，现在开始第{}次测试，老师请耐心观看，纵使会失败99次，也终将在100次会成功的!".format(i))
        if "登录成功" in success_text:
            print("在尝试了{}次后".format(i))
            print("终于登录成功啦！！！！！！！！！！")
            # 现在你可以使用success_html来访问成功页面的HTML
            break  # 如果登录成功，退出循环
        else:
            driver.quit()
            i=i+1
