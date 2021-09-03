import re
from time import sleep
import datetime
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import base64
import json
from requests import post
import os

# 此处改为自己的配置 手机号, 密码, appId
phone = 'xxxxxxxxxxx'
password = 'xxxxxx'
pid = 'xxxxxxxxxxx'

# 企业微信配置
corpid = 'xxxxxx'     # 你的企业ID
corpsecret = 'xxxxxxxx'     # Secret
agentid = 000000  # 应用AgentId
tousers = ["xxxxxx"] # 需要通知人的ID
msgtype = "textcard"
# 企业微信推送
def wxPush(title, message):
    token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?' + 'corpid=' + corpid + '&corpsecret=' + corpsecret
    req_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token='
    resp = requests.get(token_url).json()
    access_token = resp['access_token']
    data = {
        "safe": 0,
        "textcard": {
            "url": "https://cloud.tencent.com",
            "description": message,
            "title": title},
        "msgtype": msgtype,
        "touser": tousers[0],
        "agentid": agentid
    }
    data = json.dumps(data)
    req_urls = req_url + access_token
    res = requests.post(url=req_urls, data=data)

# 文件读写
def json_write(path,content):
    with open(path,"w") as f:
        json.dump(content,f)

def json_read(path):
    with open(path,'r') as f:
        load_dict = json.load(f)
        return load_dict

class FlowMonitor():

    def __init__(self):
        self.UA = None
        self.title = ''
        self.VERSION = '8.0200'
        self.request = requests.Session()
        self.resp = ''
        self.pid = pid
        self.path = "/mnt/unicom.json"
        if os.path.exists(self.path):
            self.user = json_read(self.path)
            self.newcookie = self.user[phone]["cookie"]
            newcookies = self.newcookie.split(";")
            for item in newcookies:
                if len(item)>0:
                    kv = item.split("=",1)
                    self.request.cookies[kv[0]]=kv[1]
            self.summaryFlowUsed = self.user[phone]["used"]
        else:
            self.newcookie = ""
            self.summaryFlowUsed = 0
    
    # 加密算法
    def rsa_encrypt(self, str):
        # 公钥
        publickey = '''-----BEGIN PUBLIC KEY-----
        MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDc+CZK9bBA9IU+gZUOc6
        FUGu7yO9WpTNB0PzmgFBh96Mg1WrovD1oqZ+eIF4LjvxKXGOdI79JRdve9
        NPhQo07+uqGQgE4imwNnRx7PFtCRryiIEcUoavuNtuRVoBAm6qdB0Srctg
        aqGfLgKvZHOnwTjyNqjBUxzMeQlEC2czEMSwIDAQAB
        -----END PUBLIC KEY-----'''
        rsakey = RSA.importKey(publickey)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(str.encode('utf-8')))
        return cipher_text.decode('utf-8')
    
    # 用户登录
    def login(self, mobile, passwd):
        self.UA = 'Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.99 Mobile Safari/537.36; unicom{version:android@' + self.VERSION + ',desmobile:' + mobile + '};devicetype{deviceBrand:Xiaomi,deviceModel:MI 6};{yw_code:}'
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        headers = {
            'Host': 'm.client.10010.com',
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Cookie': 'devicedId=20be54b981ba4188a797f705d77842d6',
            'User-Agent': self.UA,
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip',
            'Content-Length': '1446'
        }
        login_url = 'https://m.client.10010.com/mobileService/login.htm'
        login_data = {
            "deviceOS": "android9",
            "mobile": self.rsa_encrypt(mobile),
            "netWay": "Wifi",
            "deviceCode": "20be54b981ba4188a797f705d77842d6",
            "isRemberPwd": 'true',
            "version": "android@" + self.VERSION,
            "deviceId": "20be54b981ba4188a797f705d77842d6",
            "password": self.rsa_encrypt(passwd),
            "keyVersion": 1,
            "provinceChanel": "general",
            "appId": self.pid,
            "deviceModel": "MI 6",
            "deviceBrand": "Xiaomi",
            "timestamp": timestamp
        }

        res1 = self.request.post(login_url, data=login_data, headers=headers)
        
        res1.encoding = 'utf-8'
        try:
            result = res1.json()
            if result['code'] == '0':
                print('【'+result['default'][-4:] + '】：登录成功' + '\n')
                return True
            else:
                print('【登录】: ' + result['dsc'] + '\n')
                self.resp += '【登录】: ' + result['dsc'] + '\n'            
                return False
        except Exception as e:
            self.title = "FlowMonitor执行报错"
            self.resp +='【登录】: 发生错误，原因为: ' + str(e) + '\n'
            sleep(2)
            return False
    
    # 查询流量
    def flowMonitor(self):
        headers = {
            'Host': 'm.client.10010.com',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'User-Agent': self.UA,
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Length': '149'
        }
        data = {
            "externalSources":"",
            "contactCode":"",
            "serviceType":"",
            "saleChannel":"",
            "channelCode":"",
            "duanlianjieabc":"",
            "ticket":"",
            "ticketPhone":"",
            "ticketChannel":"",
            "userNumber":"",
            "language":"chinese"
        }
        try:
            url = "https://m.client.10010.com/servicequerybusiness/operationservice/queryOcsPackageFlowLeftContentRevisedInJune"
            res = self.request.post(url, data=data, headers=headers)
            res.encoding = 'utf-8'
            # Cookie 失效，直接返回，登录后再进行查询
            if "沃妹陪着您一起等待" in res.text:
                return False
            newcookies = self.request.cookies.items()
            for name, value in newcookies:
                self.newcookie += f'{name}={value};'
            userSummary = {}
            res = res.json()
            details = res["resources"][0]["details"]
            summary = 0
            remain = 0
            for item in details:
                self.resp += f'{item["feePolicyName"]}: 已用{item["use"]}M, 剩余{item["remain"]}M\n'
                summary += float(item["use"])
                remain += float(item["remain"])
            used = round(summary-self.summaryFlowUsed,2)
            userSummary[phone] = {
                "used": summary,
                "cookie": self.newcookie
            }
            json_write(self.path, userSummary)
            mldetails = res["MlResources"][0]["details"]
            for item in mldetails:
                # 仅查看手厅免流情况
                if item["feePolicyId"] == "10061":
                    self.resp += f'\n{item["feePolicyName"]}: 已免{item["use"]}M, 折合{str(round(float(item["use"])/1024,2))}G'
            if used>=10:
                self.title = f'💣危！{used}M! 剩余{round(remain/1024,2)}G!'
            elif used>0:
                self.title = f'⚠警！{used}M! 剩余{round(remain/1024,2)}G!'
            else:
                self.title = ""
            return True
        except Exception as e:
            self.title = "FlowMonitor执行报错"
            self.resp +='【查询】: 发生错误，原因为: ' + str(e) + '\n'
            return True
        

if __name__ == '__main__':
    user = FlowMonitor()
    if not user.flowMonitor() and user.login(phone, password):
        user.flowMonitor()
    if user.title:
        print(user.title)
        print(user.resp)
        #wxPush(user.title, user.resp)
