import requests
# 打码平台  我用的是斐斐打码
from pyfile.fateadm_api import FateadmApi
import random
import time
# 你准备的账号 一个账号最多可以推送200条域名
user_list = [{'user': 'xxxx', 'pws': 'xxxx'}, {'user': 'xxxx', 'pws': 'xxxx'},
             ]


# 打码方法
def TestFunc(path):
    # pd账号秘钥，请在用户中心页获取
    pd_id = "xx"
    pd_key = "xx"
    app_id = "xx"
    app_key = "xx"
    # 具体类型可以查看官方网站的价格页选择具体的类型，不清楚类型的，可以咨询客服
    pred_type = "30400"
    # 初始化api接口
    api = FateadmApi(app_id, app_key, pd_id, pd_key)
    res = api.PredictFromFileExtend(pred_type, path)
    return res


# 登录获取有登录状态的session
def login(user, pws):
    # 定义session
    session = requests.session()
    # 搜狗的验证码地址，必须使用session访问图片地址 登录时才有效
    img_url = f'http://zhanzhang.sogou.com/index.php/uc/vcode?tag={random.random()}'
    # 图片地址及下载图片
    filename = './vcode/' + 'verify.png'
    res = session.get(img_url)
    with open(filename, "wb") as f:
        print('开始下载')
        for chunk in res.iter_content(chunk_size=1024):
            f.write(chunk)
    # 通过打码平台获取验证码
    code = TestFunc(r'vcode/verify.png')
    # 登录地址
    url = 'http://zhanzhang.sogou.com/index.php/login'
    # 伪造请求头和post参数
    header = {
        'Host': 'zhanzhang.sogou.com',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'http://zhanzhang.sogou.com',
        'Referer': 'http://zhanzhang.sogou.com/',
    }
    data = {
        'loginForm[vcode]': code,
        'loginForm[username]': user,
        'loginForm[rememberMe]': 'on',
        'loginForm[password]': pws
    }
    # 请求地址
    req = session.post(url, headers=header, data=data)
    req.encoding = req.apparent_encoding
    print(req.text)
    # 登录成功返回session 失败返回0
    if '"success":true' in req.text:
        return session
    else:
        return 0


# 推送方法
def submit(urls, session):
    # 推送地址
    base_url = 'http://zhanzhang.sogou.com/index.php/urlSubmit/create'
    # 伪造请求头和post参数
    header = {
        'Host': 'zhanzhang.sogou.com',
        'Origin': 'http://zhanzhang.sogou.com',
        'Referer': 'http://zhanzhang.sogou.com/index.php/sitelink/index',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = {
        # urls 要推送的域名  一次最多20条  一行一个
        'webAdr': urls,
        'site_type': '1',
        'reason': '',
        'email': '换成你的联系邮箱'
    }
    req = session.post(base_url, headers=header, data=data)
    req.encoding = req.apparent_encoding
    print(req.text)
    # 推送成功返回1 失败返回0
    if '"success":true' in req.text:
        return 1
    else:
        return 0

# 我是在本地获取的域名列表 根据需求可以更改
def start():
    path = input('请输入要读取的文件名称,不用加.txt，输入1默认为data.txt')
    if path == '1':
        path = 'data'
    f = open(path + '.txt', 'r')
    datas = f.readlines()
    f.close()
    print(datas)
    return datas


if __name__ == '__main__':
    t1 = int(time.time())
    datas = start()
    num = 0
    user_num = 0
    # 第一次登录  登录成功跳出
    while True:
        session = login(user_list[user_num]['user'], user_list[user_num]['pws'])
        if session != 0:
            user_num += 1
            break
    # 开始推送
    while True:
        # 判断当前账户下标是否在账户列表内
        if user_num <= len(user_list)-1:
            # 取域名列表的20个域名
            data = datas[num:num+20]
            str1 = ''
            # 拼接推送用urls
            for i in data:
                str1 = str1 + 'http://www.' + i
            ru = submit(str1, session)
            # 推送不成功则切换账号
            if ru != 1:
                print('切换账号')
                while True:
                    session = login(user_list[user_num]['user'], user_list[user_num]['pws'])
                    if session != 0:
                        user_num += 1
                        ru = submit(str1, session)
                        if ru == 1:
                            print(f'已推送{num + 20}条,已用时{int(time.time()) - t1}秒')
                            break
            print(f'已推送{num + 20}条,已用时{int(time.time()) - t1}秒')
            # 当在域名列表取得的域名小于20条时则跳出
            if len(data) < 20:
                print(f'已推送{num + 20}条,已用时{int(time.time()) - t1}秒，全部推送完成', )
                break
            num += 20
        else:
            print(f'已推送{num + 20}条,已用时{int(time.time()) - t1}秒，账户用尽')
            break