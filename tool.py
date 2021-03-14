# -*- coding: utf-8 -*-
import json
from datetime import datetime

import requests
import traceback
import tushare as ts

# tushare pro的token以及定义pro 具体见tushare pro官网
token = '7f57fc481d8b6b1b13920cd996b2d1047723cdaf9d747ad9be4ef8ac'
pro = ts.pro_api(token)
# 聚合数据API接口
appkey = 'fe74b7a9756a5242db9d5e68061c4426'
exchangeURL = 'http://web.juhe.cn:8080/finance/exchange/rmbquot'


# 输入股票代码symbol 获得tushare代码ts_code
# 如输入600000获得600000.SH
def get_pro():
    return pro


def getdate(beforeOfDay):
    today = datetime.datetime.now()
    # 计算偏移量
    offset = datetime.timedelta(days=-beforeOfDay)
    # 获取想要的日期的时间
    re_date = (today + offset).strftime('%Y-%m-%d')
    return re_date


def getStockCode(code):
    try:
        dat = pro.query('stock_basic', fields='ts_code,symbol,name')
        stockCode = list(dat.loc[dat['symbol'] == code].ts_code)[0]
        return stockCode
    except Exception as e:
        return 0


# 输入五位代码 为其添加HK后缀
# 此步骤可能存在问题是 输入了一个不正确的H股代码 如12345 返回12345.HK 下方的getHname函数解决了这个问题
def getHStockCode(code):
    codeH = code + '.HK'
    return codeH


# 输入tushare代码ts_code 获得企业名name(简称)
def getName(code):
    try:
        dat = pro.query('stock_basic', fields='ts_code,name')
        companyName = list(dat.loc[dat['ts_code'] == code].name)[0]
        return companyName
    except:
        return "无法获取该股名称"


# 输入tushare代码ts_code 获得企业名name(全称)(A股)
def getFullName(code):
    dat = pro.query('stock_basic', fields='ts_code,fullname')
    companyName = list(dat.loc[dat['ts_code'] == code].fullname)[0]
    return companyName


# 输入tushare代码ts_code 获得企业名name(全称)(H股)
def getHname(code):
    try:
        dat = pro.hk_basic()
        companyName = list(dat.loc[dat['ts_code'] == code].fullname)[0]
        return companyName
    except Exception as e:
        if "您没有访问接口权限" in str(e):
            return str(e)
        return 0


# 废弃函数#

# 输入ts_code 获得企业名拼音
# def getPYname(code):
#    name=getName(code)
#    pyname=''
#    for i in pypinyin.pinyin(name,style=pypinyin.NORMAL,heteronym=False):#style=pypinyin.FIRST_LETTER首字母 heteronym多音字
#        pyname += ''.join(i)
#    return pyname

# 输入股票代码 判断是否为六位
def judge(code):
    if code.isdigit():  # isdigit 如果所有字符为数字Ture 不是False
        if len(code) != 6:  # 沪深股票代码为6位
            return '请输入六位股票代码'
        else:
            return 1
    else:
        return '股票代码为六位数字'


# 判断高低点填入是否为数字
def judgeHL(high, low):
    try:
        a = float(high)
        b = float(low)
        if a < 0 or b < 0:
            return 0
    except:
        return 0


# 对A股H股进行判断
def judgeAH(code):
    if code:
        if len(code) == 6:  # 沪深股票代码为6位
            return 1
        elif len(code) == 5:  # H股五位
            return 2
        else:
            return 'A股代码为六位 H股代码为五位'

    else:
        return 0


# 根据A股代码 查找H股代码
def findHcode(name):
    try:
        dat = pro.hk_basic()
        codeH = list(dat.loc[dat['fullname'] == name].ts_code)[0]
        return codeH
    except Exception as e:
        if "您没有访问接口权限" in str(e):
            return str(e)
        return '该A股为H股未上市'


# 根据H股代码 查找A股代码
def findAcode(name):
    try:
        dat = pro.query('stock_basic', fields='ts_code,fullname')
        codeA = list(dat.loc[dat['fullname'] == name].ts_code)[0]
        return codeA
    except Exception as e:
        if "您没有访问接口权限" in str(e):
            return str(e)
        return '该H股在A股未上市'


# 输入start和end 判断日期是否正确
def judgeDate(start, end):
    startDate = datetime.datetime.strptime(start, '%Y%m%d')
    endDate = datetime.datetime.strptime(end, '%Y%m%d')
    today_str = datetime.date.today().strftime('%Y%m%d')
    today = datetime.datetime.strptime(today_str, '%Y%m%d')
    if startDate >= endDate:
        return '开始日期与结束日期选择有误'
    else:
        if startDate > today or endDate > today:
            return '选择了无效日期'
        else:
            return 1


# 港币兑换为人民币汇率
# 该接口每天只能调用100次 因此加入了0.89 防止无法使用
# 理论上是不会出现错误 除非接口失效 所以不再显示messagebox 而是print出问题原因
def hdk2rmb():
    key = appkey
    url = exchangeURL
    date = {
        "key": key,
        "type": "",  # 两种格式(0或者1,默认为0)
    }
    response = requests.get(url, params=date)  # 获取数据
    res = json.loads(response.text)  # 获取的str用json形式打开 dict
    if res:
        error_code = res["error_code"]
        if error_code == 0:  # 请求成功
            exchangeRate = 1
            a = res["result"][0]  # dict
            for index, data in a.items():  # 在返回的所有币种中 找到港币
                if data["name"] == "港币":
                    print('成功获取汇率')
                    exchangeRate = float(data["bankConversionPri"])
                    return exchangeRate / 100
            if exchangeRate == 1:  # 遍历所有数据后 仍未找到港币汇率
                print('未找到港币汇率')
                return 0.89
        else:
            print('请求失败')
            return 0.89
    else:
        print('无返回内容')
        return 0.89

if __name__ == '__main__':
    code = "000063"
    findHcode(code)