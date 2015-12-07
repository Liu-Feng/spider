# -*- coding: utf-8 -*-

from spider.spiders import NewsSpider


class SinaNewsSpider(NewsSpider):
    '''新浪新闻爬虫'''

    name = 'sina_com_cn_news'
    allowed_domains = ['sina.com.cn']
    start_urls = ['http://www.sina.com.cn']

    target_urls = [
        '.*?sina\.com\.cn/\S+?/\d{4}-\d{2}-\d{2}/doc-\S+\.shtml',
        '.*?sina\.com\.cn/\d{4}-\d{2}-\d{2}/\d+.html',
        '.*?sina\.com\.cn/\S+?/\d{8}/\d+\.shtml'
    ]

    title_xpath = '//*[@id="artibodyTitle" or @id="main_title"]'
    content_xpath = '//*[@id="artibody"]'
    author_xpath = '//*[@class="show_author"]'
    author_re = u'.*?（编辑：\S+?）.*'
    publish_time_xpath = '//*[@id="pub_date" or @class="time-source"]'
    publish_time_re = u'.*?(\d{4})年(\d{2})月(\d{2})日\s*(\d{2}:\d{2}).*'
    publish_time_format = u'%Y%m%d%H:%M'
    source_xpath = '//*[@id="media_name" or @data-sudaclick="media_name"]'

    source_domain = 'sina.com.cn'
    source_name = '新浪'
