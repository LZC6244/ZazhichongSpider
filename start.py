# coding=utf-8

import os


# 将ab74_spider中的start_urls替换为要爬取的url
def str2file(newstr):
    # 声明一个空字符串用于保存ab74_spider文件内容
    s = ''
    # 打开ab74_spider文件
    with open('ZazhichongSpider/spiders/ab74_spider.py', 'r') as f:
        # 将start_urls中的网址替换为新网址
        for i in f.readlines():
            if 'start_urls' not in i:
                s += i
            else:
                i = "    start_urls = ['" + newstr + "']" + '\n'
                s += i
    with open('ZazhichongSpider/spiders/ab74_spider.py', 'w+') as f:
        f.write(s)


if __name__ == "__main__":
    print os.getcwd()
    print '=' * 25 + '杂志虫爬虫' + '=' * 25
    print '#' * 3 + ' 1.登陆杂志虫网站搜索书名'
    book_url = raw_input('#' * 3 + ' 2.请输入书籍url\n')
    # print '#' * 3 + ' 2.将书籍url输入到本爬虫'
    str2file(book_url)
    print 'spider start.'
    # 启动爬虫程序
    os.system('scrapy crawl ab74_spider')
    print 'spider end.'
