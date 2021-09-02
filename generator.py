import re
import json
import datetime
import requests

# 文档实体结构定义
class Post:

    def __init__(self,date,link,title,prefix):
        self.date  = date
        self.link  = link
        self.title = title
        self.prefix = prefix

    def getTitle(self):
        return self.title

    def getLink(self):
        return self.prefix + '/' + self.link

    def getDate(self):
        d = re.findall(r'\d{4}-\d{1,2}-\d{1,2}',self.date)[0]
        t = re.findall(r'\d{2}:\d{2}:\d{2}',self.date)[0]
        dt = '%s %s' % (d,t)
        return datetime.datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')

def loadPosts():
    response = requests.get(RECENT_POSTS_URL)
    if response.status_code == 200:
        json_data = json.loads(response.content)
        for item in json_data:
            yield Post(item['date'],item['path'],item['title'], BLOG_URL_PREFIX)
    else:
        return []

# 常量定义
TO_REPLACE_TAG = '{{Recent Posts}}'
BLOG_URL_PREFIX = 'https://blog.yuanpei.me'
RECENT_POSTS_URL = 'https://blog.yuanpei.me/content.json'

def formatPost(item):
    itemTpl = '* {0} - [{1}]({2})'
    return itemTpl.format(
        datetime.datetime.strftime(item.getDate(),'%Y-%m-%d'),
        item.getTitle(),
        item.getLink()
    )

with open('./README.md', 'wt', encoding='utf-8') as fw:
    with open('./.template/README.md', 'rt', encoding='utf-8') as fr:
      posts = sorted(loadPosts(),key=lambda x:x.getDate(),reverse=True)
      recent_posts = ''
      if len(posts) > 0:
         recent_posts = '\n'.join(list(map(lambda x: formatPost(x), posts[:7])))
      content = fr.read().replace(TO_REPLACE_TAG, recent_posts)
      fw.write(content)