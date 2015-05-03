# About PyCrawlers

自己写的一些python小爬虫

## weibo_album

windows下的新浪微博相册爬虫，可以下载整个微相册的照片，默认是下载原图，可以修改代码进行设置。因为微相册是动态加载的，所以用了[phantomjs](http://phantomjs.org/)来获取网页源码，
使用python的[selenium](https://pypi.python.org/pypi/selenium)来进行调用。  
*   用法  
首先修改`weibo_album.py`中的`phantomjs.exe`的路径，然后`python weibo_album.py [options] [args]`  
*   参数说明：   
```
-u  username    新浪微博帐号，必须，只有登录后才能查看微相册
-p  password    新浪微博密码，必须
-s  search_user 要下载的微相册的主人的用户名，由于是在微博搜索中搜索用户，并直接选择搜索结果中的   
                第1个用户，所以尽可能是全名。当不存在 -a 参数时，会默认选择用户的“微博配图”相册进行下载
-a  album_url   要下载的微相册的链接地址（必须是在微相册的“列表模式”下，这也是微相册的默认模式），  
                存在时会直接访问该地址进行下载，与 -s 二者有其一即可   
-m  min_size    下载的图片大小的最小值(单位: byte)，可选，默认102400byte
-t  top         下载默认相册“微博配图”或指定微相册链接下的最新的top张照片，可选，默认整个相册
```
 
