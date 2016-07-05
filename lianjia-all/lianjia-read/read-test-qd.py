#!/usr/bin/python
# -*- coding:utf-8 -*-
# regex_spider.py
# author: song


import zlib
import struct
from bs4 import BeautifulSoup as bs
import traceback
import re




if __name__ == "__main__":
    soup = bs(open('index.html'))
    content = soup.find("ul", "house-lst")
    list = content.find_all("li")
    for i in list:
        name = i.find("div", "info-panel").next_element.get_text().encode('utf-8').strip()
        rent = i.find("div", "col-1").find_all("a")[0].get_text().encode('utf-8').replace("套正在出租", "").strip()
        lal = i.find("div", "other")
        locate1 = lal.find_all("a")[0].get_text().encode('utf-8').strip()
        locate2 = lal.find_all("a")[1].get_text().encode('utf-8').strip()
        build  = lal.find_all("span")[0].next_sibling.encode('utf-8')
        year = lal.find_all("span")[1].next_sibling.encode('utf-8').replace("建造", "").strip()
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
                #print subwayl
                subst = subwayl[1].strip()
            elif subway.count("）"):
                subwayl = subway.split("）", 1)
                subline = subwayl[0].replace("近地铁", "") + ")"
                #print subwayl
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
        total = name + "|"+ rent + "|" + locate1 + "|" + locate2 + "|" +build+ "|" + price + "|" + sale + "|" + year + "|" + school + "|" + subline.strip() + "|" + subst + "\n"








        print total
    num = soup.find("div", "con-box").find("span").get_text()
    print int(num),type(int(num))
        #print "\n"
    #courseInfo=soup.find(attrs={ "class": "house-lst"})
    #print courseInfo.find_all('a')
    #course=soup.find_all("a","actshowMap_list")
    #print course
    #for text in course:
    #    print(text.get('platename'))
    #for text in courseInfo.find_all('a'):
     #   print(text.get_text())
    #file_object_Z.write(courseInfo)
    #file_object_Z.close()
    #file_object_Z.write(soup.find_all("div","info-panel"))
    #print soup.find_all('h2')
    #for tag in soup.find_all(re.compile("^b")):
    #print(tag.name)
    #file_object_Z.close()



    #finally:
        #file_object_Z.close()
    print "ok!"