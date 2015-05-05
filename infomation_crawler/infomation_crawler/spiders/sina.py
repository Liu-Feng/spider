from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from infomation_crawler.items import WebArticleItem
import datetime
import pymongo
import re

class SinaSpider(CrawlSpider):
  name = 'sina'
  allowed_domains = ['sina.com.cn']
  start_urls = ['http://tech.sina.com.cn/']

  conn = pymongo.Connection('localhost',27017)
  infoDB = conn.info
  tWebArticles = infoDB.web_articles

  rules = (
    Rule(SgmlLinkExtractor(allow=r'tech\.sina\.com\.cn'), callback='parse_item'),
  )

  def parse_item(self, response):
    print "enter sina_parse_item...."
    sel = Selector(response)
    i = WebArticleItem()
    
    title = sel.xpath('//h1[@id="artibodyTitle"]/text()').extract()
    i['title'] = len(title)>0 and title[0].strip() or ''

    i['url'] = response.url

    publishTime = re.findall(r'\d{4}-\d{2}-\d{2}', i['url'], re.M)
    if len(publishTime)>0:
      i['publishTime'] = publishTime[0]
    else:
      i['publishTime'] = str(datetime.date.today())
    source = sel.xpath('//span[@id="media_name"]/a/text()').extract()
    i['source'] = len(source)>0 and source[0] or ''
    author = sel.xpath('//span[@id="author_ename"]/a/text()').extract()
    i['author'] = len(author)>0 and author[0] or ''
    
    i['abstract'] = ''
    
    keyWordList = sel.xpath('//p[@class="art_keywords"]/a/text()').extract()
    keyWords = len(keyWordList)>0 and keyWordList[0].strip() or ''
    for key in range(len(keyWordList)-1):
      keyWords = keyWords + '|' + keyWordList[key+1].strip()
    i['keyWords'] = keyWords

    content = sel.xpath('//div[@id="artibody"]').extract()
    i['content'] = len(content)>0 and content[0] or ''

    i['siteName'] = 'sina'

    i['addTime'] = datetime.datetime.now()

    return i