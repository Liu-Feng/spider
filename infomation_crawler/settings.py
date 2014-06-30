# Scrapy settings for infomation_crawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'infomation_crawler'

SPIDER_MODULES = ['infomation_crawler.spiders']
NEWSPIDER_MODULE = 'infomation_crawler.spiders'
DEFAULT_ITEM_CLASS = 'infomation_crawler.BaiduNewsItem'

ITEM_PIPELINES = {'infomation_crawler.pipelines.InfomationCrawlerPipeline': 1}
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'infomation_crawler (+http://www.yourdomain.com)'
