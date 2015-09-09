# -*- coding: utf-8 -*-
import re

def filterTags(htmlstr):
        #先过滤CDATA  
        re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA  
        re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script  
        re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style  
        re_br=re.compile('<br\s*?/?>')#处理换行  
        re_h=re.compile('</?\w+[^>]*>')#HTML标签  
        re_comment=re.compile('<!--[^>]*-->')#HTML注释  
        s=re_cdata.sub('',htmlstr)#去掉CDATA  
        s=re_script.sub('',s) #去掉SCRIPT  
        s=re_style.sub('',s)#去掉style  
        s=re_br.sub('',s)#将br转换为换行  
        s=re_h.sub('',s) #去掉HTML 标签  
        s=re_comment.sub('',s)#去掉HTML注释  
        #去掉多余的空行  
        blank_line=re.compile('\n+')
        s=blank_line.sub('',s)
        return s