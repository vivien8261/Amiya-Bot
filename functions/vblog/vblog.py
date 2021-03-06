import os
import re
import time
import requests

from message.messageType import Image
from modules.commonMethods import Reply, remove_xml_tag

user_id = '6279793937'


class VBlog:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) '
                          'AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
            'Content-Type': 'application/json; charset=utf-8',
            'Referer': 'https://m.weibo.cn/u/%s' % user_id,
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        self.url = 'https://m.weibo.cn/api/container/getIndex?uid=%s&type=uid&value=%s' % (user_id, user_id)

    def get_cards_list(self):
        session = requests.session()

        # 获取微博 container id
        result = session.get(self.url, headers=self.headers).json()

        if 'tabsInfo' not in result['data']:
            return []

        tabs = result['data']['tabsInfo']['tabs']
        container_id = ''
        for tab in tabs:
            if tab['tabKey'] == 'weibo':
                container_id = tab['containerid']

        # 获取正文列表
        result = session.get(self.url + '&containerid=%s' % container_id, headers=self.headers).json()

        cards = []
        for item in result['data']['cards']:
            if item['card_type'] == 9 and 'isTop' not in item['mblog']:
                cards.append(item)

        return cards

    def get_blog_list(self):

        cards = self.get_cards_list()

        text = '博士，这是【明日方舟Arknights】最近的微博列表。\n'

        for index, item in enumerate(cards):
            content = remove_xml_tag(item['mblog']['text'])
            content = content[:30].replace('\n', ' ').replace('#明日方舟#', '').strip()

            date = item['mblog']['created_at']
            date = time.strptime(date, '%a %b %d %H:%M:%S +0800 %Y')
            date = time.strftime('%m-%d %H:%M', date)

            text += '\n【%d】%s\n --- %s…' % (index + 1, date, content)

        text += '\n\n请和我说「阿米娅查看第 N 条微博」来获取详情吧'

        return Reply(text)

    def requests_content(self, only_id=False, index=0):
        session = requests.session()

        cards = self.get_cards_list()

        if index >= len(cards):
            return Reply('博士，只能获取到列表内的微博哦')

        target_blog = cards[index]
        blog = target_blog['mblog']
        detail_url = target_blog['scheme']
        item_id = target_blog['itemid']

        if only_id:
            return item_id

        # 获取完整正文
        url = 'https://m.weibo.cn/statuses/extend?id=%s' % blog['id']
        result = session.get(url, headers=self.headers).json()
        html_text = result['data']['longTextContent']
        html_text = re.sub('<br />', '\n', html_text)
        html_text = remove_xml_tag(html_text)
        html_text = html_text.strip('\n')

        # 获取静态图片列表
        pics_list = []
        pics = blog['pics'] if 'pics' in blog else []
        for pic in pics:
            pic_url = pic['large']['url']
            name = pic_url.split('/')[-1]
            suffix = name.split('.')[-1]
            if suffix.lower() == 'gif':
                continue
            temp = 'resource/message/Blog'
            path = '%s/%s' % (temp, name)
            if os.path.exists(path) is False:
                if os.path.exists(temp) is False:
                    os.mkdir(temp)
                stream = requests.get(pic_url, headers=self.headers, stream=True)
                if stream.status_code == 200:
                    open(path, 'wb').write(stream.content)

            pics_list.append(Image(path))

        return [
            Reply(html_text),
            Reply(detail_url, 0, at=False, auto_image=False),
            Reply(pics_list, 0, at=False)
        ]
