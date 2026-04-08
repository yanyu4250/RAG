import requests


#定义url
target_url = "https://www.tiobe.com/tiobe-index/"

#发送请求获取数据
aa = requests.get(target_url)

print(aa.text)
