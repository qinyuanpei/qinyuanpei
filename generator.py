import re
import json
import pytz
import datetime
import requests
import feedparser

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
        if self.prefix == '' or self.prefix == None:
           return self.link
        else:
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

def loadPostsByRSS():
    feed = feedparser.parse(POSTS_RSS_URL)
    for item in feed.entries:
        publish_date = datetime.datetime.strptime(item.published, '%a, %d %b %Y %H:%M:%S +0000')
        publish_date = datetime.datetime.strftime(publish_date,'%Y-%m-%d %H:%M:%S')
        yield Post(publish_date, item.link, item.title, None)

# 常量定义
POSTS_RSS_URL = 'https://blog.yuanpei.me/index.xml'

TO_REPLACE_POSTS = '{{Recent Posts}}'
TO_REPLACE_DATE = '{{Generated At}}'

BLOG_URL_PREFIX = 'https://blog.yuanpei.me'
RECENT_POSTS_URL = 'https://blog.yuanpei.me/content.json'

RECENT_POST_LIMIT = 10


# 时区定义
tz = pytz.timezone('Asia/Shanghai')

def formatPost(item):
    itemTpl = '* {0} - [{1}]({2})'
    return itemTpl.format(
        datetime.datetime.strftime(item.getDate(),'%Y-%m-%d'),
        item.getTitle(),
        item.getLink()
    )

with open('./README.md', 'wt', encoding='utf-8') as fw:
    with open('./.template/README.md', 'rt', encoding='utf-8') as fr:
      posts = sorted(loadPostsByRSS(), key=lambda x:x.getDate(),reverse=True)
      recent_posts = ''
      if len(posts) > 0:
         recent_posts = '\n'.join(list(map(lambda x: formatPost(x), posts[:RECENT_POST_LIMIT])))
      content = fr.read().replace(TO_REPLACE_POSTS, recent_posts)
      createdAt = datetime.datetime.now(tz)
      createdAt = datetime.datetime.strftime(createdAt,'%Y-%m-%d %H:%M:%S')
      content = content.replace(TO_REPLACE_DATE, createdAt)
      fw.write(content)