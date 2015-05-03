# About PyCrawlers

自己写的一些python小爬虫

## weibo_album

windows下的新浪微博相册爬虫，可以下载整个微相册的照片，并将本次下载失败的图片链接保存在`failed_download_urls.txt`，默认是下载原图，可以修改代码进行设置。因为微相册是动态加载的，所以用了[phantomjs](http://phantomjs.org/)来获取网页源码，
使用python的[selenium](https://pypi.python.org/pypi/selenium)来进行调用。  
###功能
1.   在微博搜索中搜索指定的用户名，选择结果中第1个用户，所以用户名越准确越好，默认下载其“微博配图”相册。
2.   可以指定微博相册的链接地址，此时无论是否设置了要搜索的用户名，都会直接访问该地址进行下载，要求**必须**是微博相册的“列表模式”下的链接地址，其链接类似于`http://photo.weibo.com/2206258462/talbum/index?from=profile_wb#!/mode/1/page/1`，`mode`后的参数为**1**，这也是微博相册的默认模式。   
3.   可以设置下载图片大小的最小值，单位为byte，默认为`102400byte`，即`100kb`。
4.   可以设置下载图片的数量N，此时会下载“微博配图”相册或指定相册链接地址内的前N张照片，默认会下载当前相册当前页面及以后的所有照片，不设置相册链接地址时会从“微博配图”相册首页开始下载全部照片。
5.   默认下载原图，相册“列表模式”下的图片是小图，其链接地址中有`small`字样，当`download_image()`中`large`为`True`时会通过`re.sub`将`small`替换为`large`来下载原图，将代码中调用`download_image()`时的`large`改为`False`就能下载小图了。   

###用法  
修改`weibo_album.py`中的`phantomjs.exe`的路径   
`python weibo_album.py [options] [args]`  
*   参数说明：   
```
-u  username    新浪微博帐号，必须，只有登录后才能查看微相册
-p  password    新浪微博密码，必须
-s  search_user 要下载的微相册的主人的用户名。当不存在 -a 参数时，会默认选择用户的“微博配图”相册进行下载
-a  album_url   要下载的微相册的链接地址，与 -s 二者有其一即可   
-m  min_size    下载的图片大小的最小值(单位: byte)，可选，默认102400byte
-t  top         下载默认相册“微博配图”或指定微相册链接下的最新的top张照片，可选，默认全部照片
```
 
