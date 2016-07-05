#!/usr/bin/python
# -*- coding:utf-8 -*-
# regex_spider.py
# author: song

import cookielib
import cookielib
import os
import random
import re
import socket
import struct
import sys
import time
import traceback
import urllib
import httplib
from httplib import IncompleteRead
import urllib2
import zlib
from posixpath import normpath
from urlparse import urljoin
from urlparse import urlparse
from urlparse import urlunparse

from socket import timeout

from bs4 import BeautifulSoup


class regexSpider:
    doneUrls = [ ]
    doneall = set([])
    downnum = int(0)
    totalnum = int(0)

    def get_pagenum(self , page):
        soup = BeautifulSoup ( page )
        pagelist = soup.find ( "div" , "page-box house-lst-page-box" )
        numlist = pagelist.get ( 'page-data' )
        totalPage = eval ( numlist )[ 'totalPage' ]
        curPage = eval(numlist)['curPage']
        return totalPage,curPage

    def analysis(self , page):
        alltotal=[]
        soup = BeautifulSoup(page, "lxml")
        content = soup.find ( "ul" , "house-lst" )
        list = content.find_all ( "li" )
        for i in list:
            name = i.find("div", "info-panel").next_element.get_text().encode('utf-8').strip()
            saler = \
            i.find("div", "col-1").find_all("a")[0].get_text().encode('utf-8').replace("90天成交", "").split("套", 1)[
                0].replace(" ", "").strip()
            rent = i.find("div", "col-1").find_all("a")[1].get_text().encode('utf-8').replace("套正在出租", "").strip()
            lal = i.find("div", "other")
            locate1 = lal.find_all("a")[0].get_text().encode('utf-8').strip()
            locate2 = lal.find_all("a")[1].get_text().encode('utf-8').strip()
            year = lal.find_all("span")[0].next_sibling.encode('utf-8').replace("建造", "").strip()
            chanquan = i.find("div", "chanquan")
            if chanquan.find("span", "fang05-ex"):
                school = chanquan.find("span", "fang05-ex").get_text().encode('utf-8').strip()
            else:
                school = ""
            if chanquan.find("span", "fang-subway-ex"):
                subway = chanquan.find("span", "fang-subway-ex").get_text().encode('utf-8')
                if subway.count(")"):
                    subwayl = subway.split(")", 1)
                    subline = subwayl[0].replace("近地铁", "") + ")"
                    # print subwayl
                    subst = subwayl[1].strip()
                elif subway.count("）"):
                    subwayl = subway.split("）", 1)
                    subline = subwayl[0].replace("近地铁", "") + ")"
                    # print subwayl
                    subst = subwayl[1].strip()
                else:
                    subwayl = subway.split("线", 1)
                    subline = subwayl[0].replace("近地铁", "") + "线"
                    subst = subwayl[1].strip()


            else:
                subway = ""
                subline = ""
                subst = ""
            price = i.find("span", "num").get_text().encode('utf-8')
            sale = i.find("div", "square").find("span", "num").get_text().encode('utf-8')
            total = name + "|" + saler + "|" + rent + "|" + locate1 + "|" + locate2 + "|" + price + "|" + sale + "|" + year + "|" + school + "|" + subline.strip() + "|" + subst + "\n"
            alltotal.append(total)
        return alltotal



            # 使用Request
    def get_request(self , url , referUrl):
        # print "get: "+url+", refer:"+referUrl
        # 可以设置超时
        socket.setdefaulttimeout ( 30 )
        # 可以加入参数	[无参数，使用get，以下这种方式，使用post]
        params = {"wd": "a" , "b": "2"}
        # 可以加入请求头信息，以便识别
        i_headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5" , "Accept": "*/*" , "Referer": referUrl}
        # use post,have some params post to server,if not support ,will throw exception
        # req = urllib2.Request(url, data=urllib.urlencode(params), headers=i_headers)
        # 创建MozillaCookieJar实例对象
        cookie = cookielib.MozillaCookieJar ( )
        # 从文件中读取cookie内容到变量
        cookie.load ( 'cookie.txt' , ignore_discard=True , ignore_expires=True )
        req = urllib2.Request ( url , headers=i_headers )

        # 创建request后，还可以进行其他添加,若是key重复，后者生效
        # request.add_header('Accept','application/json')
        # 可以指定提交方式
        # request.get_method = lambda: 'PUT'
        try_count = 0
        while 1:
            if try_count >= 10:
                return None,None
            try:
                # page = urllib2.urlopen(req)
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
                page = urllib2.urlopen(req).read().decode('utf-8')
                pageUrl = url
                #return page, pageUrl
                break
            except (urllib2.HTTPError, urllib2.URLError,  httplib.BadStatusLine, IncompleteRead, timeout):
                try_count += 1
                print('error occurred, reloading %s time: %s... ' % (try_count, url))
                continue
        return page, pageUrl

        '''
        try:
            # page = urllib2.urlopen(req)
            opener = urllib2.build_opener ( urllib2.HTTPCookieProcessor ( cookie ) )
            page = urllib2.urlopen ( req ).read ( ).decode ( 'utf-8' )
            pageUrl = url
            return page , pageUrl
        except urllib2.HTTPError , e:
            print "Error Code:" , e.code
        except urllib2.URLError , e:
            print "Error Reason:" , e.reason
        except:
            print traceback.format_exc ( )
        return None , None
        '''


            # 下载并写入一个url


    def downAndWriteOneUrl(self , baikeUrl , referUrl , file_object_Z , bWrite):
        try:
            srcHtml , pageUrl = self.get_request ( baikeUrl , referUrl )
            if (srcHtml != None and pageUrl != None):
                baikeUrl = pageUrl
                if (bWrite):
                    print "save page: " + baikeUrl
                    baikeHtml = srcHtml  # zlib.compress(srcHtml)
                    htmlLen = struct.pack ( "L" , len ( baikeHtml ) )

                    urlLen = struct.pack ( "L" , len ( baikeUrl ) )
                    allmes=self.analysis(baikeHtml)
                    for i in allmes:
                        if (i not in self.doneall):
                            self.downnum = self.downnum+1
                            file_object_Z.write ( i )
                            self.doneall.add(i)
                            print "downnum:",self.downnum
                            #print i

                    #file_object_Z.write ( urlLen )
                    #file_object_Z.write ( baikeUrl )

                    #file_object_Z.write ( htmlLen )
                    #file_object_Z.write ( baikeHtml )

            return baikeUrl , srcHtml
        except IOError , e:
            print "IOError:" , e
        except:
            print traceback.format_exc ( )
        return None , None


        # url拼接，相对路径转换为绝对路径


    def myjoin(self , base , url):
        url1 = urljoin ( base , url )
        arr = urlparse ( url1 )
        path = normpath ( arr[ 2 ] )
        return urlunparse ( (arr.scheme , arr.netloc , path , arr.params , arr.query , arr.fragment) )


        # 抓取递归处理函数


    def crawlPages(self , url , referUrl , downUrlReg , writeUrlReg , ignoreUrlReg , file_object_Z , deepMax , deepCnt):
        deepCnt += 1
        if (deepCnt >= deepMax):  # 进行爬行深度限定
            return

        if (url not in self.doneUrls):
            self.doneUrls.append ( url )
            print str ( deepCnt ) + " - deal page: " + url
            bWrite = False
            if (writeUrlReg.match ( url ) != None):
                bWrite = True
            downUrl,srcHtml = self.downAndWriteOneUrl ( url , referUrl , file_object_Z , bWrite )
            #print "downUrl : " + downUrl

            if (downUrl != None and srcHtml != None):
                soup = BeautifulSoup ( srcHtml, "lxml" )
                if (soup != None):
                    # 提取 /subview 链接
                    totalPage, curPage = self.get_pagenum(srcHtml)
                    if totalPage ==100:
                        links = soup.find("div","filter-box").findAll('a')
                        toDoUrls = []
                        for link in links:
                            subUrl = link.get('href')
                            if subUrl != None:
                                if subUrl.startswith('http') == False:  # 相对链接
                                    subUrl = self.myjoin(downUrl, subUrl)
                                # print "subUrl : "+subUrl
                                if (downUrlReg.match(subUrl) != None) and (
                                    ignoreUrlReg.match(subUrl) == None):  # 需要且不是过滤链接
                                    self.crawlPages(subUrl, downUrl, downUrlReg, writeUrlReg, ignoreUrlReg,
                                                    file_object_Z, deepMax, deepCnt)
                                    '''
                                    if curPage == 1:
                                        for pagenum in range(totalPage):
                                            if subUrl.endswith('/'):
                                                url = subUrl + 'pg' + '%s' % (pagenum + 1)
                                                self.crawlPages(url, subUrl, downUrlReg, writeUrlReg, ignoreUrlReg,
                                                                file_object_Z, deepMax, deepCnt)
                                            else:
                                                url = subUrl + '/pg' + '%s' % (pagenum + 1)
                                                self.crawlPages(url, subUrl, downUrlReg, writeUrlReg, ignoreUrlReg,
                                                                file_object_Z, deepMax, deepCnt)

                                    elif not curPage:
                                        self.crawlPages(subUrl, downUrl, downUrlReg, writeUrlReg, ignoreUrlReg,
                                                        file_object_Z, deepMax, deepCnt)
                                    '''
                    else:
                        if curPage == 1:
                            numll = soup.find("div", "con-box").find("span").get_text()
                            num = int(numll)
                            self.totalnum = self.totalnum + num
                            print 'this page number:', num, 'totalnum', self.totalnum
                            for pagenum in range(totalPage):
                                if downUrl.endswith('/'):
                                    url = downUrl + 'pg' + '%s' % (pagenum + 1)
                                else:
                                    url = downUrl + '/pg' + '%s' % (pagenum + 1)
                                if (downUrlReg.match(url) != None) and (
                                    ignoreUrlReg.match(url) == None):        # 需要且不是过滤链接
                                    self.crawlPages(url, downUrl, downUrlReg, writeUrlReg, ignoreUrlReg,file_object_Z, deepMax, deepCnt)
                        elif not curPage:
                            self.crawlPages(downUrl, downUrl, downUrlReg, writeUrlReg, ignoreUrlReg, file_object_Z,
                                            deepMax, deepCnt)


    # 爬行抓取工作函数
    # 参数列表：
    # 		起始url列表
    # 		下载中间url正则
    #		写文件url正则
    #		写文件名称
    def spiderWorking(self , startUrlList , downUrlRegex , writeUrlRegex , ignoreUrlRegex , writeFileName , deepMax):
        downUrlReg = re.compile ( downUrlRegex )
        writeUrlReg = re.compile ( writeUrlRegex )
        ignoreUrlReg = re.compile ( ignoreUrlRegex )
        file_object_Z = open ( writeFileName , "wb" )
        file_object_Z.write("小区名|90天成交套数|出租数|所属区|区域|均价|在售数|年份|学区|地铁线|地铁站")
        file_object_Z.write("\n")

        try:
            for startUrl in startUrlList:
                self.crawlPages ( startUrl , startUrl , downUrlReg , writeUrlReg , ignoreUrlReg , file_object_Z , deepMax , 0 )
                # sleepSec = random.randrange(3,8)
                # time.sleep(sleepSec)

        finally:
            file_object_Z.close ( )


    # file_object.close()
    def readDataFile(self , dataFileName):
        print sys.getdefaultencoding ( )
        file_object_Z = open ( dataFileName , "rb" )
        try:
            nDictCnt = 0
            while True:
                urlLen = struct.unpack ( "L" , file_object_Z.read ( 4 ) )
                srcUrl = file_object_Z.read ( urlLen[ 0 ] )

                htmlLen = struct.unpack ( "L" , file_object_Z.read ( 4 ) )
                zipHtml = file_object_Z.read ( htmlLen[ 0 ] )
                srcHtml = zipHtml  # zlib.decompress(zipHtml)

                if (srcUrl.find ( 'http://pinyin.sogou' ) >= 0):
                    print str ( nDictCnt ) + " - " + srcUrl
                    dictNav = ""
                    soup = BeautifulSoup ( srcHtml , from_encoding='gbk' )
                    if (soup != None):
                        bcNav = soup.find ( 'div' , {'class': 'bcnav'} )
                        if (bcNav != None):
                            # print bcNav.text.decode('gbk')
                            dictNav = bcNav.text.encode ( 'gbk' , 'ignore' )  # .encode('utf-8')
                            # print dictNav
                        dlInfoBox = soup.find ( 'div' , {'class': 'dlinfobox'} )
                        if (dlInfoBox != None):
                            links = dlInfoBox.findAll ( 'a' )
                            for link in links:
                                subUrl = link.get ( 'href' )
                                if (re.match ( ".*download_cell\.php.*" , subUrl ) != None):
                                    print subUrl
                                    # srcHtml, pageUrl = self.get_request(subUrl,str(srcUrl))
                                    # print len(srcHtml)

                    nDictCnt += 1
                    print str ( nDictCnt ) + " - " + str ( dictNav ) + " - " + srcUrl

        # print srcHtml
        # break

        except IOError , e:
            print "IOError:" , e
        except:
            print traceback.format_exc ( )
        finally:
            file_object_Z.close ( )


    def unzipDataFile(self , dataFileName , unzipFileName):
        print sys.getdefaultencoding ( )
        file_object_Z = open ( dataFileName , "rb" )
        file_object_W = open ( unzipFileName , "wb" )
        try:
            nDictCnt = 0
            while True:
                urlLen = struct.unpack ( "L" , file_object_Z.read ( 4 ) )
                srcUrl = file_object_Z.read ( urlLen[ 0 ] )

                htmlLen = struct.unpack ( "L" , file_object_Z.read ( 4 ) )
                zipHtml = file_object_Z.read ( htmlLen[ 0 ] )
                srcHtml = zlib.decompress ( zipHtml )

                htmlLen = struct.pack ( "L" , len ( srcHtml ) )

                urlLen = struct.pack ( "L" , urlLen[ 0 ] )
                file_object_W.write ( urlLen )
                file_object_W.write ( srcUrl )

                file_object_W.write ( htmlLen )
                file_object_W.write ( srcHtml )
                # print srcHtml
                # break

        except IOError , e:
            print "IOError:" , e
        except:
            print traceback.format_exc ( )
        finally:
            file_object_Z.close ( )
            file_object_W.close ( )  # 主函数
if __name__ == "__main__":
    # splider=BrowserBase()
    # splider.openurl('http://download.pinyin.sogou.com/dict/download_cell.php?id=15206&name=%B6%AF%CE%EF%B4%CA%BB%E3%B4%F3%C8%AB%A1%BE%B9%D9%B7%BD%CD%C6%BC%F6%A1%BF')

    reload ( sys )
    sys.setdefaultencoding ( 'utf-8' )
    if (os.path.exists ( 'data/' ) == False):
        os.mkdir ( 'data/' )

    urllist="http://hz.lianjia.com/xiaoqu/"

    startUrlList = [ urllist ]
    # ["http://pinyin.sogou.com/dict/"]
    downUrlRegex =(urllist+"([a-z]{2,20})")+"|"+(urllist+"([a-z]{2,20})/pg[0-9]{1,2}")
    #r"(http://bj.lianjia.com/xiaoqu/([a-z]{2,20}))|(http://bj.lianjia.com/xiaoqu/([a-z]{2,20})/pg[0-9]{1,2})"
    # "(http://pinyin\.sogou\.com/dict/list\.php.*)|(http://download\.pinyin\.sogou\.com/dict/download_cell\.php.*)|(http://pinyin\.sogou\.com/dict/cell\.php\?id=.*)"
    writeUrlRegex = urllist+"([a-z]{2,20})/pg[0-9]{0,4}"
    #r"(http://bj.lianjia.com/xiaoqu/([a-z]{2,20})/pg[0-9]{0,4})"
    # "(http://pinyin\.sogou\.com/dict/cell\.php\?id=.*)|(http://download\.pinyin\.sogou\.com/dict/download_cell\.php.*)"
    ignoreUrlRegex = "(.*author\.php.*)|(.*search\.php.*)|(.*goto\.php.*)|(.*#top)|(.*rs.*)|(.*j[0-9]{1,10}.*)|(.*y[0-9]{1,10}.*)|(.*w[0-9]{1,10}.*)|(.*t[0-9]{1,10}.*)|(.*s[0-9]{1,10}.*)|(.*p[0-9]{1,10}.*)|(.*su[0-9]{1,10}.*)|(.*sc[0-9]{1,10}.*)|(.*cro[0-9]{1,10}.*)|(.*pg[0-9]{1,10}/pg[0-9]{1,10}.*)"

    writeFileName = "data/result.txt"

    # writeReg = re.compile(ignoreUrlRegex)
    # testUrl = "http://pinyin.sogou.com/dict/search.php?word=%C4%A7%CA%DE%CA%C0%BD%E7&page=2"
    # if(writeReg.match(testUrl) != None):
    #	print "write Match" + testUrl
    # else:
    #	print "write Not Match" + testUrl

    mySpider = regexSpider ( )

    '''
    仅下载指定列表url
    file_object_Z = open("leftSogouDict.dat", "wb")
    file = open("willDownload.txt")
    try:
        while 1:
            line = file.readline()
            if not line:
                break
            mySpider.downAndWriteOneUrl(line,line,file_object_Z,True)

    finally:
        file_object_Z.close()
        file.close()
    '''
    # mySpider.readDataFile(writeFileName)
    # mySpider.readDataFile("data/unzip_sogou.dat")
    # mySpider.unzipDataFile(writeFileName,"data/unzip_sogou.dat")

    mySpider.spiderWorking ( startUrlList , downUrlRegex , writeUrlRegex , ignoreUrlRegex , writeFileName , 10)
    print "All Done!"
