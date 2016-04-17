#!/usr/bin/python
# -*- coding:utf-8 -*-
# regex_spider.py
# author: song

import urllib,urllib2,cookielib,socket
import time
import random
import zlib
import struct
import re,os,sys
from bs4 import BeautifulSoup as bs
import traceback

from urlparse import urljoin
from urlparse import urlparse
from urlparse import urlunparse
from posixpath import normpath
import csv

class regexSpider:
	doneUrls = []

	#使用Request
	def get_request(self, url):
		#print "get: "+url+", refer:"+referUrl
		#可以设置超时
		socket.setdefaulttimeout(30)
		sleepSec = random.randrange(6, 10)
		time.sleep(sleepSec)
		#可以加入参数	[无参数，使用get，以下这种方式，使用post]
		params = {"wd":"a","b":"2"}
		enable_proxy = True
		proxy = urllib2.ProxyHandler({"http": "http://222.95.249.189:8090"})
		proxy_support = urllib2.ProxyHandler({})
		opener = urllib2.build_opener(proxy)
		urllib2.install_opener(opener)
		#可以加入请求头信息，以便识别
		i_headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5","Accept": "*/*"}
		cookie = cookielib.MozillaCookieJar()
		cookie.load('cookie.txt', ignore_discard=True, ignore_expires=True)
		#use post,have some params post to server,if not support ,will throw exception
		#req = urllib2.Request(url, data=urllib.urlencode(params), headers=i_headers)
		req = urllib2.Request(url, headers=i_headers)

		#创建request后，还可以进行其他添加,若是key重复，后者生效
		#request.add_header('Accept','application/json')
		#可以指定提交方式
		#request.get_method = lambda: 'PUT'
		try:
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
			page = opener.open(req)
			data = page.read()
			pageUrl = page.geturl()
			page.close()
			return data,pageUrl
		except urllib2.HTTPError, e:
			print "Error Code:", e.code
		except urllib2.URLError, e:
			print "Error Reason:", e.reason
		except :
			print traceback.format_exc()

	#下载并写入一个url
	def downAndWriteOneUrl(self, baikeUrl,file_object_Z, bWrite): #file_object_X,file_object_Y,
		try:
			srcHtml, pageUrl = self.get_request(baikeUrl)
			sleepSec = random.randrange(3, 8)
			time.sleep(sleepSec)
			if(srcHtml != None and pageUrl != None):
				baikeUrl = pageUrl
				if(bWrite):
					print "save page: " + baikeUrl
					baikeHtml = srcHtml#zlib.compress(srcHtml)
					soup = bs(baikeHtml, "lxml")
					page = soup.find("div", "left680")
					title = page.find("h1", "left_h1").get_text()
					table = page.find("tbody").find_all("tr")
					ilist = []
					for i in table:
						for j in i.find_all("td"):
							if j.get("class") == None:
								ilist.append(j.get_text())
					deal = '|'.join(ilist)
					dit = page.find("h4", "cw").next_siblings
					#print dit
					for i in dit:
						if i:
							if i.string:
								dis = i.replace("\n", "").replace(" ", "").replace("\t", "").replace("\r", "")
								print dis
					message = baikeUrl + '|' + title + '|' + deal+ '|'

					#file_object_X.writerow([str(baikeUrl)])
					#file_object_Y.writerow([str(page)])
					file_object_Z.write(message+dis)
					file_object_Z.write("\n")

			return baikeUrl,srcHtml
		except IOError, e:
			print "IOError:", e
		except :
			print traceback.format_exc()
		return None,None

	#url拼接，相对路径转换为绝对路径
	def myjoin(self, base, url):
		url1 = urljoin(base, url)
		arr = urlparse(url1)
		path = normpath(arr[2])
		return urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))

	#抓取递归处理函数
	def crawlPages(self, url,downUrlReg,writeUrlReg,ignoreUrlReg,file_object_Z,deepMax,deepCnt):
		deepCnt += 1
		if(deepCnt >= deepMax):#进行爬行深度限定
			return

		if(url not in self.doneUrls):
			self.doneUrls.append(url)
			print str(deepCnt)+" - deal page: "+url
			bWrite = False
			if(writeUrlReg.match(url) != None):
				bWrite = True
			downUrl,srcHtml = self.downAndWriteOneUrl(url,referUrl,file_object_Z,bWrite)
			#print "downUrl : "+downUrl

			if(downUrl != None and srcHtml != None):
				soup = BeautifulSoup(srcHtml)
				if(soup != None):
					#提取 /subview 链接
					links = soup.findAll('a')
					toDoUrls = []
					for link in links:
						subUrl = link.get('href')
						if subUrl != None:
							if subUrl.startswith('http') == False :#相对链接
								subUrl = self.myjoin(downUrl,subUrl)
							print "subUrl : "+subUrl
							if downUrlReg.match(subUrl) != None:#需要处理
								if(ignoreUrlReg.match(subUrl) == None): #且不是过滤链接
									self.crawlPages(subUrl,downUrl,downUrlReg,writeUrlReg,ignoreUrlReg,file_object_Z,deepMax,deepCnt)

	# 爬行抓取工作函数
	# 参数列表：
	# 		起始url列表
	# 		下载中间url正则
	#		写文件url正则
	#		写文件名称
	def spiderWorking(self, startUrlList, downUrlRegex, writeUrlRegex,ignoreUrlRegex, writeFileName ,deepMax):
		downUrlReg = re.compile(downUrlRegex)
		writeUrlReg = re.compile(writeUrlRegex)
		ignoreUrlReg = re.compile(ignoreUrlRegex)
		file_object_Z = open(writeFileName, "wb")
		try:
			for startUrl in startUrlList:
				self.crawlPages(startUrl,startUrl,downUrlReg,writeUrlReg,ignoreUrlReg,file_object_Z,deepMax,0)
				#sleepSec = random.randrange(3,8)
				#time.sleep(sleepSec)

		finally:
			file_object_Z.close()
			#file_object.close()
	def readDataFile(self, dataFileName):
		print sys.getdefaultencoding()
		file_object_Z = open(dataFileName, "rb")
		try:
			nDictCnt = 0
			while True:
				urlLen = struct.unpack("L",file_object_Z.read(4))
				srcUrl = file_object_Z.read(urlLen[0])

				htmlLen = struct.unpack("L",file_object_Z.read(4))
				zipHtml = file_object_Z.read(htmlLen[0])
				srcHtml = zipHtml#zlib.decompress(zipHtml)

				if(srcUrl.find('http://pinyin.sogou') >= 0):
					print str(nDictCnt) +" - " + srcUrl
					dictNav = ""
					soup = BeautifulSoup(srcHtml,from_encoding='gbk')
					if(soup != None):
						bcNav = soup.find('div',{'class':'bcnav'})
						if(bcNav != None):
							#print bcNav.text.decode('gbk')
							dictNav = bcNav.text.encode('gbk', 'ignore')#.encode('utf-8')
							#print dictNav
						dlInfoBox = soup.find('div',{'class':'dlinfobox'})
						if(dlInfoBox != None):
							links = dlInfoBox.findAll('a')
							for link in links:
								subUrl = link.get('href')
								if(re.match(".*download_cell\.php.*",subUrl) != None):
									print subUrl
									#srcHtml, pageUrl = self.get_request(subUrl,str(srcUrl))
									#print len(srcHtml)

					nDictCnt += 1
					print str(nDictCnt) +" - "+ str(dictNav) +" - " + srcUrl

				#print srcHtml
				#break

		except IOError, e:
			print "IOError:", e
		except :
			print traceback.format_exc()
		finally:
			file_object_Z.close()
	def unzipDataFile(self, dataFileName, unzipFileName):
		print sys.getdefaultencoding()
		file_object_Z = open(dataFileName, "rb")
		file_object_W = open(unzipFileName, "wb")
		try:
			nDictCnt = 0
			while True:
				urlLen = struct.unpack("L",file_object_Z.read(4))
				srcUrl = file_object_Z.read(urlLen[0])

				htmlLen = struct.unpack("L",file_object_Z.read(4))
				zipHtml = file_object_Z.read(htmlLen[0])
				srcHtml = zlib.decompress(zipHtml)

				htmlLen = struct.pack("L",len(srcHtml))

				urlLen = struct.pack("L",urlLen[0])
				file_object_W.write(urlLen)
				file_object_W.write(srcUrl)

				file_object_W.write(htmlLen)
				file_object_W.write(srcHtml)
				#print srcHtml
				#break

		except IOError, e:
			print "IOError:", e
		except :
			print traceback.format_exc()
		finally:
			file_object_Z.close()
			file_object_W.close()

#主函数
if __name__ == "__main__":
	#splider=BrowserBase()
	#splider.openurl('http://download.pinyin.sogou.com/dict/download_cell.php?id=15206&name=%B6%AF%CE%EF%B4%CA%BB%E3%B4%F3%C8%AB%A1%BE%B9%D9%B7%BD%CD%C6%BC%F6%A1%BF')

	reload(sys)
	sys.setdefaultencoding('utf-8')
	'''
	if(os.path.exists('data/') == False):
		os.mkdir('data/')

	startUrlList = ["http://shanghai.anjuke.com/community/"]

	downUrlRegex = "(http://pinyin\.sogou\.com/dict/list\.php.*)|(http://download\.pinyin\.sogou\.com/dict/download_cell\.php.*)|(http://pinyin\.sogou\.com/dict/cell\.php\?id=.*)"
	writeUrlRegex = "(http://pinyin\.sogou\.com/dict/cell\.php\?id=.*)|(http://download\.pinyin\.sogou\.com/dict/download_cell\.php.*)"
	ignoreUrlRegex = "(.*author\.php.*)|(.*search\.php.*)|(.*goto\.php.*)"

	writeFileName = "data/sogou.dat"

	#writeReg = re.compile(ignoreUrlRegex)
	#testUrl = "http://pinyin.sogou.com/dict/search.php?word=%C4%A7%CA%DE%CA%C0%BD%E7&page=2"
	#if(writeReg.match(testUrl) != None):
	#	print "write Match" + testUrl
	#else:
	#	print "write Not Match" + testUrl
	'''
	mySpider = regexSpider()
	if (os.path.exists('china/') == False):
		os.mkdir('china/')
	#writeFileName1 = "url.csv"
	#writeFileName2 = "page.csv"
	#仅下载指定列表url
	result = open("chinaresult.txt", "wb")
	#csvfile1 = file(writeFileName1, 'wb')
	#csvfile2 = file(writeFileName2, 'wb')
	#file_object_X = csv.writer(csvfile1, delimiter='|')
	#file_object_Y = csv.writer(csvfile2, delimiter='|')
	file = open("chinalist.txt")
	result.write('url|标题|投资时间|地区|企业阶段|融资性质|融资金额|股权|企业估值|行业分类|融资方|投资方|投资银行|律师事务所|会计事务所|描述')
	result.write("\n")

	try:
		while 1:
			line = file.readline()
			line1=line.replace('\n','' )
			result.flush()
			if not line1:
				break


			mySpider.downAndWriteOneUrl(line1,result,True)  #,file_object_X,file_object_Y



	finally:
		#csvfile1.close()
		#csvfile2.close()
		result.close()
		file.close()

	#mySpider.readDataFile(writeFileName)
	#mySpider.readDataFile("data/unzip_sogou.dat")
	#mySpider.unzipDataFile(writeFileName,"data/unzip_sogou.dat")

	#mySpider.spiderWorking(startUrlList,downUrlRegex,writeUrlRegex,ignoreUrlRegex,writeFileName,200)
	print "All Done!"