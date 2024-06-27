import requests
from bs4 import BeautifulSoup
session = requests.session()

url ='https://login2.scrape.center/'
response_before = session.get(url)
soup = BeautifulSoup(response_before.text, 'html.parser')

username_input = soup.find('input', {'name': 'username'})['name']
password_input = soup.find('input', {'name': 'password'})['name']

data = {
    username_input: 'admin',
    password_input: 'admin',
}

form_action = "https://login2.scrape.center/login"
response_later = session.post(form_action, data=data)
content_later = response_later.text

# 比较内容是否发生了变化
if content_later != response_before.text:
    print("成功登录！")
    print(content_later)
    print("任务完成！")
else:
    print("登录失败")
