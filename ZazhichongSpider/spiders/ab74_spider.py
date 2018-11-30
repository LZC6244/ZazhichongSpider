# -*- coding: utf-8 -*-
import scrapy
import re
import sys
from scrapy import Request

# 重载sys,设置编码为utf-8,解决中文编码乱码
reload(sys)
sys.setdefaultencoding('utf-8')


class Ab74SpiderSpider(scrapy.Spider):
    '''
    需要通过爬取第一章之后不断前往下一页爬取,不能直接从书籍目录页获取所有章节url
    因为有部分章节在目录不显示(隐藏了)
    直接从目录页爬取会导致章节缺失
    '''
    name = 'ab74_spider'
    allowed_domains = ['www.ab74.com']
    start_urls = ['https://www.ab74.com/book/4293.shtml']
    # 书籍本地txt文件名
    book_name_txt = ''

    def parse(self, response):
        # 书名
        book_name = response.xpath('//div[@class="title"]/h1/text()').extract()[0]

        # 作者名
        author_name = response.xpath('//li[@class="odd"][1]/p/text()').extract()[0]
        author_name.replace(' ', '')

        # 字数
        word_num = response.xpath('//li[@class="odd"][2]/p/text()').extract()[0]
        # 取出字数中的数字
        pattern = re.compile('\d+')
        word_num = re.search(pattern, word_num).group()
        # 将字数从unicode转换为int型
        word_num = int(word_num)
        # 将字数除以10000
        word_num = word_num / 10000
        word_num = str(word_num) + '万字'

        # 最新一章章节名
        chapter_name = response.xpath('//p[@class="short_de"]/a/text()').extract()[0]

        # txt书名为：书名@作者名@字数@最新章节名
        self.book_name_txt = book_name + '@' + author_name + '@' + word_num + '@' + chapter_name
        # 当前字符串编码为unicode，将其转换为utf-8,才可与'./小说/'和'.txt'拼接
        self.book_name_txt = self.book_name_txt.encode('utf-8')
        self.book_name_txt = './小说/' + self.book_name_txt + '.txt'

        # 书籍目录页url
        book_catalog_url = response.xpath('//a[@class="read blue"]/@href').extract()[0]
        print book_catalog_url

        request = Request(url=book_catalog_url, callback=self.parse_catalog, dont_filter=True)
        yield request

    def parse_catalog(self, response):
        # 第一章url
        first_chapter_url = response.xpath('//div[@class="dir_main_section"]/ol[1]/li[1]/a/@href').extract()[0]
        first_chapter_url = 'https://www.ab74.com' + str(first_chapter_url)
        print first_chapter_url

        request = Request(url=first_chapter_url, callback=self.parse_detail, dont_filter=True)
        yield request

    def parse_detail(self, response):

        if not response.xpath('//div[@class="divimage"]'):
            # 判断能否还存在下一章,存在则继续往下爬取
            if response.xpath('//a[@id="pager_next"]/@href'):
                # 章节名
                chapter_title = response.xpath('//div[@class="chapter_title"]/h2/text()').extract()[0]
                # 章节内容列表
                chapter_content_list = response.xpath('//div[@id="inner"]/text()').extract()
                # 下一章url
                next_chapter_url = response.xpath('//a[@id="pager_next"]/@href').extract()[0]
                next_chapter_url = 'https://www.ab74.com' + str(next_chapter_url)

                print chapter_title + 'crawl start.'

                # 用来存储章节内容的字符串
                chapter_content_str = ''
                for i in chapter_content_list:
                    chapter_content_str += i

                # 将本章节内容存入txt文件
                with open(self.book_name_txt, 'a') as f:
                    # [杂志虫]网站只有部分章节内容含有章节名称,不能使用下面这种方式写如txt文件
                    # 会导致后面章节内容缺失标题
                    # f.write(chapter_content_str)
                    f.write('\n' + chapter_title + '\n' + chapter_content_str)

                print chapter_title + 'crawl end.'

                request = Request(url=next_chapter_url, callback=self.parse_detail, dont_filter=True)
                yield request
            else:
                print '=' * 15 + '本书所有章节(已更新)爬取完毕.' + '=' * 15
        else:
            print '=' * 15 + '剩下的是图片章节,不做爬取.' + '=' * 15
