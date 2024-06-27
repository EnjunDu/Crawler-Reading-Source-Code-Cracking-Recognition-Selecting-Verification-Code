import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import ddddocr

# 使用Selenium获取验证码图片和文本
driver = webdriver.Chrome()
driver.maximize_window()
url = 'https://captcha8.scrape.center/'
i=0
while True:
    i=i+1
    driver.get(url)

    # 捕获验证码图像
    captcha_element = driver.find_element(By.ID, "captcha")
    captcha_image_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", captcha_element)

    with open("captcha.png", "wb") as file:
        file.write(base64.b64decode(captcha_image_base64))

    ocr = ddddocr.DdddOcr()
    with open("captcha.png", 'rb') as f:
        img_bytes = f.read()
    captcha_text = ocr.classification(img_bytes)
    if i>1:
        print("呜呜呜，上一个验证码错惹")
    print("验证码为:", captcha_text)

    # 查找用户名输入字段
    username_input = driver.find_element(By.XPATH, '//div[contains(@class, "el-tooltip") and contains(@class, "username")]/input[@class="el-input__inner"]')

    # 查找密码输入字段
    password_input = driver.find_element(By.XPATH, '//div[contains(@class, "el-tooltip") and contains(@class, "password")]/input[@class="el-input__inner"]')

    # 查找验证码输入字段
    captcha_input = driver.find_element(By.XPATH, '//div[contains(@class, "captcha")]/input[@class="el-input__inner"]')

    # 输入用户名、密码和验证码
    username_input.send_keys('admin')
    password_input.send_keys('admin')
    captcha_input.send_keys(captcha_text)

    # 查找登录按钮
    login_button = driver.find_element(By.CLASS_NAME, 'el-button--primary')

    # 点击登录按钮
    login_button.click()

    time.sleep(5)

    success_element = driver.find_elements(By.XPATH, '//h2[@data-v-55ca188a and @class="text-center"]')
    if success_element:
        success_text = success_element[0].text
        if "登录成功" in success_text:
            print("终于登录成功啦！！！！！！！！！！")
            break

driver.quit()
