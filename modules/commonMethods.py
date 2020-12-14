import os
import re
import sys
import json

from message.messageType import MessageType
from library.imageCreator import create_image
from modules.resource.imageManager import ImageManager

MSG = MessageType()
IM = ImageManager('resource/message/Common/')

with open('config.json') as conf:
    config = json.load(conf)


class Reply:
    def __init__(self, content, feeling=2, sign=0, at=True, auto_image=True):

        if isinstance(content, str):
            content = content.strip('\n')

        if auto_image and isinstance(content, str) and len(content) >= config['message']['reply_text_max_length']:
            image = create_image(content, 'Common')
            image_id = IM.image(image)
            self.content = [MSG.image(image_id)]
        else:
            self.content = content

        self.feeling = feeling
        self.sign = sign
        self.at = at


def list_split(items: list, n: int):
    return [items[i:i + n] for i in range(0, len(items), n)]


def word_in_sentence(sentence: str, words: list):
    for word in words:
        if word in sentence:
            return True
    return False


def check_sentence_by_re(sentence: str, words: list, names: list):
    for item in words:
        for n in names:
            if re.search(re.compile(item % n if '%s' in item else item), sentence):
                return True
    return False


def all_item_in_text(text: str, items: list):
    for item in items:
        if item not in text:
            return False
    return True


def insert_empty(text, max_num, half=False):
    return '%s%s' % (text, ('　' if half else ' ') * (max_num - len(str(text))))


def restart():
    python = sys.executable
    os.execl(python, python, *sys.argv)