# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from optparse import OptionParser
import time
import sys,os
import re
import urllib,urllib2

album_dir = os.path.join(os.getcwd(),'albums');

class Weibo:
    def __init__(self, username, password, search_user = None, album_url = None, min_size = 102400, top = None):
        self.username = username
        self.password = password
        self.search_user = search_user
        self.album_url = album_url#only for weibo album url
        self.min_size = min_size
        self.top = top
        self.mainHandler = None 
        self.driver = webdriver.PhantomJS(executable_path=r'F:\python\phantomjs-2.0.0-windows\bin\phantomjs.exe')#the path of phantomjs.exe in windows
        self.driver.maximize_window()#browser full screen

    def __login(self):
        self.driver.get("http://login.sina.com.cn/signup/signin.php?entry=sso")#sina passport
        self.driver.find_element_by_xpath('//input[@name="username"]').clear()
        self.driver.find_element_by_xpath('//input[@name="username"]').send_keys(self.username)
        self.driver.find_element_by_xpath('//input[@name="password"]').send_keys(self.password)

        time.sleep(2)
        self.driver.get_screenshot_as_file('loin.png')
        self.driver.find_element_by_xpath('//input[@type="submit"]').click()

        try:
            dr=WebDriverWait(self.driver,5)
            dr.until(lambda the_driver:the_driver.find_element_by_xpath('//a[@href="http://weibo.com"]').is_displayed())
        except:
            print 'login weibo failed'
            sys.exit(0)
        else:
            print 'login weibo success'

    def __search(self):
        self.driver.get("http://s.weibo.com/")#weibo search
        self.driver.find_element_by_xpath('//a[@action-data="type=user"]').click()
        self.driver.find_element_by_xpath('//input[@class="searchInp_form"]').send_keys(self.search_user.decode('gbk'))# windows cmd is GBK encoded
        self.driver.find_element_by_xpath('//a[@node-type="submit"]').click()
        try:
            dr=WebDriverWait(self.driver,5)
            dr.until(lambda the_driver:the_driver.find_element_by_xpath('//a[@suda-data="key=tblog_search_user&value=user_feed_1_icon"]').is_displayed())
        except:
            print 'search user failed'
            sys.exit(0)

        #this click will open a new window
        nowhandle = self.driver.current_window_handle
        self.driver.find_element_by_xpath('//a[@suda-data="key=tblog_search_user&value=user_feed_1_icon"]').click()#first searched user is user_feed_1_icon，the second is user_feed_2_icon, ...
        allhandles = self.driver.window_handles
        newhandler = nowhandle
        for handle in allhandles:#find the new window handler
            if handle != nowhandle:
                newhandler = handle
                break
        if newhandler == nowhandle:
            print 'open weibo mainpage failed in a new window failed'
            sys.exit(0)
        else:
            self.driver.close()
            self.driver.switch_to_window(newhandler)
        
        try:
            dr=WebDriverWait(self.driver,5)
            dr.until(lambda the_driver:the_driver.find_element_by_xpath('//a[@suda-uatrack="key=tblog_profile_new&value=tab_album"]').is_displayed())
        except:
            print 'open weibo mainpage failed'
            sys.exit(0)
        else:
            print 'open weibo mainpage success'


    def __open_defaut_album(self):
        self.driver.find_element_by_xpath('//a[@suda-uatrack="key=tblog_profile_new&value=tab_album"]').click()
        try:
            dr=WebDriverWait(self.driver,5)
            dr.until(lambda the_driver:the_driver.find_element_by_xpath('//a[@title="微博配图"]').is_displayed())
        except:
            print 'can not find default album'
            sys.exit(0)

        #this click will open a new window
        self.mainhandle = self.driver.current_window_handle#mainhandler is searched user's weibo mainpage
        self.driver.find_element_by_xpath('//a[@title="微博配图"]').click()
        allhandles = self.driver.window_handles
        newhandler = self.mainhandle
        for handle in allhandles:
            if handle != self.mainhandle:
                newhandler = handle
                break
        if newhandler == self.mainhandle:
            print 'open default album in a new window failed'
            sys.exit(0)
        else:
            print 'open weibo default album success'
            self.driver.switch_to_window(newhandler)

    def __open_specify_album(self):
        #only support list mode of weibo album, like 'http://.../mode/1/...'
        self.driver.get(self.album_url)
        try:
            album = self.driver.find_element_by_xpath('//div[@class="m_bread_crumb"]/a').text
        except:
            print 'get album username failed'

        self.search_user = re.sub(u'的专辑','',album).encode('gbk') if album else 'Temp'


    def download_album(self):

        self.__login()
        if not self.album_url:
            self.__search()
            self.__open_defaut_album()
        else:
            self.__open_specify_album()
        
        page = 1
        if not self.top:
            self.top = float("inf") #infinite
        wb_image = WeiboImage(self.search_user, self.min_size, self.top)
        while(1):
            try:
                dr=WebDriverWait(self.driver,5)
                dr.until(lambda the_driver:the_driver.find_element_by_xpath('//ul[@class="photoList clearfix"]').is_displayed())
            except:
                print 'load images failed'
                sys.exit(0)

            
            image_urls = wb_image.get_image_url(self.driver.page_source)
            image_count, failed_download_urls = wb_image.download_image(image_urls)
            print 'album page %s done, download %s images' % (page, image_count)
            if image_count >= self.top:
                break
            page += 1
            try:
                self.driver.find_element_by_xpath('//a[@class="M_btn_c next"]').click()
            except:
                break
        print 'all done!'
        try:
            log = open('failed_download_urls.txt','w')
            for url in failed_download_urls:
                log.write(url.encode('utf-8'))
                log.write('\n')
        except Exception, e:
            print 'log write failed: %s' % e                          
        log.close
        self.driver.quit()


class WeiboImage:
    def __init__(self, album_name, min_size = 102400, top = None):
        self.album_name = album_name
        self.album_path = os.path.join(album_dir, album_name)
        self.min_size = min_size
        self.top = top
        self.failed_download_urls = []
        self.image_count = 0

        if not os.path.isdir(self.album_path):
            os.makedirs(self.album_path)

    def get_image_url(self, html):
        self.image_urls = []
        try:
            
            r_img = re.compile(r'src=[\'|\"]((http://|https://|).*?/small/.*?\.(gif|jpg|png|jpeg|bmp))[\'|\"]')
            
            for imgurl in r_img.findall(html):
                if not imgurl[1]:
                    continue#skip relative path
                else:
                    imgurl = imgurl[0]
                self.image_urls.append(imgurl)
        except Exception, e:
            print 'parase image url error: %s' % e
            sys.exit(0)
        else:
            return self.image_urls

    def download_image(self, urls, large = True):
        for url in urls:
            try:
                if large:
                    url = re.sub('small', 'large', url)
                connection = urllib2.build_opener().open(urllib2.Request(url))
                if int(connection.headers.dict['content-length']) < self.min_size:
                    continue
                data = urllib.urlopen(url).read()
            except Exception, e:
                print 'connect error: %s' % e
                self.failed_download_urls.append(url)
                continue
            image_name = url.split('/')[-1]
            image_name += '' if len(image_name.split('.')) == 2 else '.jpg'#if image_name have no type, add .jpg
            image_path = os.path.join(self.album_path, image_name.encode("utf-8"))
            image = open(image_path,'wb')
            try:
                image.write(data)
            except Exception, e:
                print 'save image failed: %s' % e
                self.failed_download_urls.append(url)
            else:
                self.image_count += 1
            image.close
            del image
            if self.image_count >= self.top:
                break
            time.sleep(0.01)
        return self.image_count, self.failed_download_urls

def main(args):

    usage = "usage: %prog [options] [args]"
    parser = OptionParser(usage=usage)
    parser.add_option("-u", "--username",
                      dest="username", help="your weibo username [essential]")
    parser.add_option("-p", "--password",
                      dest="password", help="your weibo password [essential]")
    parser.add_option("-s", "--search_user",
                      dest="search_user", help="the weibo user you want to search [essential if no -a]")
    parser.add_option("-a", "--album_url",
                      dest="album_url", help="the weibo album url you want to download [essential if no -s]")
    parser.add_option("-m", "--min_size",
                      default="102400",type="int",dest="min_size",
                      help="min_size (byte) of download image,default is 102400 byte [optional]")
    parser.add_option("-t", "--top",
                      type="int",dest="top",
                      help="the top newest images to download [optional]")

    if type(args) == str:
        args = args.split()

    (options, args) = parser.parse_args(args)

    if not options.username or not options.password:
        print 'you must input your weibo username and password to login'
        return False
    if not options.album_url:
        if not options.search_user:
            print 'you must input the user you want to search or the album url'
            return False

    wb = Weibo(options.username, options.password, options.search_user, options.album_url, options.min_size, options.top)
    wb.download_album()

if __name__ == '__main__':

    main(sys.argv)
