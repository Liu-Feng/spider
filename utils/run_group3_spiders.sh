#!/bin/sh

echo "run group3 spiders...."
cd /data0/sourcecode/information_crawler/group3
for i in abi baisejiadiantieba bbscheaa cena ea3w hc360 hea163 jdbbs jdwxinfo newscheaa smarthomeqianjia
do
	#curl http://172.20.8.163:6800/schedule.json -d project=group3 -d spider=${i}
	scrapy crawl $i
done