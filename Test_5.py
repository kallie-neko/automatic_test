# -*- coding: UTF-8 -*-

'''
公司目前需要大量的人脸图像来进行算法训练，要求为同一人的多张照片。现在假设有一目标网站：https://www.uumnt.com/chemo/该网站的车模美女是符合要求的，点击每个车模图片可以看到该车模的多张图片。
现编写一个简易爬虫程序，将该网站上的车模图片全部下载下来，同一个车模的图片放在同一个文件夹下。
'''

import threading
import requests
from bs4 import BeautifulSoup
import time
import os
import urllib
import json
import base64
import matplotlib.pyplot as plt
import shutil

detectFaceUrl = r'http://10.2.33.52:8080/fr-oms/interface/idetectFace'
# 下载图片的路径
dirpathname = r'F:\images_test'
# 无效人脸的路径
notfacedir = r'F:\image_notface'

# 获取车模图片地址
def findUrls(root_url):
    S = requests.Session()
    target_headers = {'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer':'http://www.xicidaili.com/nn/',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
    }
    url=[]
    # 根据页码循环获取车模链接
    for i in range(1,16):
        print('Now get the %s picture url!In order to not be find Maybe need more time'%i)
        # 爬取列表页
        target_url=root_url+str(i)+'.html'
        target_response = S.get(url = target_url, headers = target_headers)
        target_response.encoding = 'utf-8'
        html = target_response.text
        # 解析html
        soup=BeautifulSoup(html, 'html.parser',from_encoding= 'utf8')
        # print(soup)
        # 获取当前页的车模链接
        urls=soup.find("div", id="mainbodypul")
        urls=urls.find_all('a')
        for j in range(0,len(urls),2):
            url.append('https://www.uumnt.com'+urls[j].attrs['href'])
            # print('https://www.uumnt.com'+urls[j].attrs['href'])
            time.sleep(2)
    return url

# 下载车模所有图片
def getClassUrl(targeturl):
    S = requests.Session()
    target_headers = {'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer':'http://www.xicidaili.com/nn/',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'zh-CN,zh;q=0.8',
        }
    # 爬取车模图片页
    target_url=targeturl
    target_response = S.get(url = target_url, headers = target_headers)
    target_response.encoding = 'utf-8'
    html = target_response.text
    soup=BeautifulSoup(html, 'html.parser',from_encoding= 'utf8')
    urls=soup.find("div", class_="page")
    urls=urls.find_all('a')
    # 获取当前车模总图片数
    urls1=urls[len(urls)-1].attrs['href'].split('_')[1]
    urls2=urls[len(urls)-1].attrs['href'].split('_')[0]+'_'
    rooturl='https://www.uumnt.com'+urls2
    page=urls1.split('.')[0]
    dirpath = ''
    # 下载车模图片
    for i in range(1,int(page)+1):
        picture_url=rooturl+str(i)+'.html'
        target_response = S.get(url = picture_url, headers = target_headers)
        target_response.encoding = 'utf-8'
        html = target_response.text
        soup=BeautifulSoup(html, 'html.parser',from_encoding= 'utf8')
        urls=soup.find_all("img")[1]
        # 获取当前页面车模图片的src
        pictureurl=urls.attrs['src']
        print(pictureurl)
        picturename=urls.attrs['src'].split('/')[5]
        # 每个车模创建一个图片保存目录
        dirpath = dirpathname + '\\' + picturename
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        # 定义每张车模图片的路径
        filepath = dirpath + '\\' + picturename + '_' + str(i) + '.jpg'
        urllib.request.urlretrieve(pictureurl, filepath)
        # urllib.request.urlretrieve(pictureurl,'D:\images\%s\%s.jpg'%(picturename,str(i)))
        time.sleep(2)

# 检测图片是否存在人脸
def detectFace(detectFaceUrl, filepath):
    try:
        fp = open(filepath, 'rb')  # 二进制方式打开图文件
        fpBase64 = base64.b64encode(fp.read())

        field = {'faceImgs': fpBase64.decode('utf-8')}
        requestData = json.dumps(field)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(detectFaceUrl, headers=headers, data=requestData)

        strResult = response.content.decode("UTF-8")
        rspJsonData = json.loads(strResult)

        if '0' != rspJsonData['result']:
            return False
        return True
    except Exception as ex:
        return False

# 计算有效图片的数量
def countImage(dirpath):
    dirHash = {}
    resultHash = {}
    dirList = os.listdir(dirpath)
    print(dirList)
    # 读取文件夹内文件路径
    for i in dirList:
        dirHash[i] = os.listdir(os.path.join(dirpath,i))
    # print(dirHash)
    size = 0
    # 循环读取每张图片
    for key in dirHash.keys():
        count = 0
        print(key)
        for i in dirHash[key]:
            imagepath = os.path.join(dirpath,key,i)
            # 检测图片是否存在人脸，是则计数加1，否则移动图片到notfacedir目录下
            code = detectFace(detectFaceUrl, imagepath)
            # print(imagepath)
            # print(code)
            if code:
                count += 1
                # 统计图片的大小
                size = os.path.getsize(imagepath)
            else:
                print(imagepath)
                shutil.move(imagepath,notfacedir)
                # s.remove(imagepath)
        if 0 == count:
            os.rmdir(os.path.join(dirpath, key))
        else:
            resultHash[key] = count
    # resultHash = {文件夹名：有效图片数}
    return resultHash,size

# 绘制折线图
def drawPicture(resultHash):
    x = []
    y = []
    diclist = sorted(resultHash)
    for i in diclist:
        x.append(i)
        y.append(resultHash[i])

    plt.plot(x,y)

    plt.title('imageCount')
    plt.xlabel('image')
    plt.ylabel('count')

    plt.show()

if __name__ == '__main__':
    root_url = 'https://www.uumnt.com/chemo/list_'
    # 采集车模图片地址
    target_urls=findUrls(root_url)
    print(target_urls)
    # 下载图片
    n = len(target_urls) // 4 +1
    for i in range(0, n):
        t1 = threading.Thread(target=getClassUrl, name='LoopThread %s' % i, args=(target_urls[i],))
        t1.start()
        t2 = threading.Thread(target=getClassUrl, name='LoopThread %s' % i, args=(target_urls[i+1],))
        t2.start()
        t3= threading.Thread(target=getClassUrl, name='LoopThread %s' % i, args=(target_urls[i+2],))
        t3.start()
        t4= threading.Thread(target=getClassUrl, name='LoopThread %s' % i, args=(target_urls[i+3],))
        t4.start()

    # 处理下载的图片

    # resultHash,size = countImage(dirpathname)
    # print(resultHash)
    # # 用折线图展示每个车模拥有的图片数量
    # drawPicture(resultHash)
    # # 打印有效车模的总人数
    # print('有效车模的总人数为：',len(resultHash))
    # # 打印所有图片文件夹的总大小
    # print('所有图片文件夹的总大小为：',size)
