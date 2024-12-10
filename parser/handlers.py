import json
import hashlib
import uuid
import logging
from multiprocessing import Pool
from io import BytesIO
from datetime import datetime, timedelta

from urllib import parse
from PIL import Image

import boto3
import requests

import db

from .parsers import PARSERS

from models.parser import ParsedItem, Advert, Link

from settings import settings


logging.getLogger('boto3').setLevel(logging.WARNING)

session = boto3.session.Session()
client = session.client('s3', region_name=settings.DO_SPACE_REGION,
                        endpoint_url=f'https://{settings.DO_SPACE_REGION}.digitaloceanspaces.com',
                        aws_access_key_id=settings.DO_SPACE_KEY,
                        aws_secret_access_key=settings.DO_SPACE_SECRET)

WIDTH = 320
HEIGHT = 230


def _load_image(item, folder_name):
    image = item.get('image')
    if image:
        try:
            response = requests.get(image, stream=True)
            img = Image.open(BytesIO(response.content))
            hsize = int(float(img.size[1]) * float(WIDTH) / float(img.size[0]))
            if hsize >= HEIGHT:
                img = img.resize((WIDTH, hsize), Image.LANCZOS)
                delta = hsize - HEIGHT if hsize > HEIGHT else 0
                img = img.crop((0, delta / 2, WIDTH, hsize - (delta / 2)))
            elif hsize < HEIGHT:
                wsize = int(float(img.size[0]) * float(HEIGHT) / float(img.size[1]))
                img = img.resize((wsize, HEIGHT), Image.LANCZOS)
                delta = wsize - WIDTH if wsize > WIDTH else 0
                img = img.crop((delta / 2, 0, wsize - (delta / 2), HEIGHT))
            else:
                # If not height resize with auto height
                img = img.resize((WIDTH, hsize), Image.LANCZOS)
            output = BytesIO()
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(output, 'webp', quality=75)
            output.seek(0)
            filename = uuid.uuid4()
            client.upload_fileobj(output, settings.DO_SPACE_NAME, f'{folder_name}/{filename}.webp',
                                  ExtraArgs={'ContentType': 'image/webp', 'ACL': 'public-read'})
            item['image'] = \
                f"https://{settings.DO_SPACE_NAME}.{settings.DO_SPACE_REGION}.digitaloceanspaces.com/{folder_name}/{filename}.webp"
        except Exception as e:
            logging.error(e)
    return item


def load_advert_image(item):
    return _load_image(item, 'adv')


def load_news_image(item):
    return _load_image(item, 'news')


# For future usage
def load_images(items, func):
    with Pool(5) as p:
        items = p.map(func, items)
    return items


def delete_old_images(offset=0):
    _session = db.Session()
    for item in _session.query(Advert).filter(
            Advert.created < datetime.now() - timedelta(days=8)).order_by(Advert.created.desc()).limit(1000).offset(
        offset):
        data = json.loads(item.data)
        image = data.pop("image", '')
        if image and f"https://{settings.DO_SPACE_NAME}.{settings.DO_SPACE_REGION}.digitaloceanspaces.com" in image:
            try:
                client.delete_object(
                    Bucket=settings.DO_SPACE_NAME,
                    Key=image.replace(
                        f"https://{settings.DO_SPACE_NAME}.{settings.DO_SPACE_REGION}.digitaloceanspaces.com/", ''))
            except Exception as e:
                logging.error(e)
        item.data = json.dumps(data)
    _session.commit()


class ParseHandler(object):

    def __init__(self, map_instance, session=None):
        self.map = map_instance
        self.session = db.Session() if session is None else session

    def create_items(self):
        tt = list()
        to_create = list()
        for i in PARSERS.get(self.map.type)(self.map).get_items():
            item = self.get_item(i)
            if item:
                to_create.append(item)
                tt.append(i)
        self.session.add_all(to_create)
        self.session.commit()
        return tt

    def get_item_hash(self, i):
        _map = json.loads(self.map.map)
        _map.pop('encode', None)
        return hashlib.md5((':'.join([i.get(k, "") for k in _map.keys()]) + self.map.link).encode()).hexdigest()

    def is_new(self, _hash):
        q = self.session.query(ParsedItem).filter(ParsedItem.hash == _hash)
        return not self.session.query(q.exists()).scalar()

    def get_item(self, data):
        _hash = self.get_item_hash(data)
        if self.is_new(_hash):
            data = _load_image(data, 'news')
            return ParsedItem(hash=_hash, category_id=self.map.category_id, data=json.dumps(data))


class LinkParseHandler(ParseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0

    def create_items(self):
        to_create = list()
        for items in PARSERS.get(self.map.type)(self.map):
            # If more than ten parsed items just skip
            if self.counter >= 10:
                break
            for i in items:
                item = self.get_item(i)
                if item:
                    to_create.append(item)
            self.session.add_all(to_create)
            self.session.commit()
            to_create = list()

    def is_new(self, link):
        q = self.session.query(Link).filter(Link.link == link)
        return not self.session.query(q.exists()).scalar()

    def get_item(self, data):
        # Clean link before checking
        _link = parse.urlparse(data["link"])
        _link = f'{_link.scheme}://{_link.netloc}{_link.path}'
        if self.is_new(_link):
            return Link(link=_link)
        self.counter += 1


class AdvertParseHandler(ParseHandler):
    def create_adverts(self):
        for link in self.session.query(Link).filter(Link.is_parsed.is_(False)).filter(
                Link.link.contains(self.map.host)):
            item = PARSERS.get(self.map.type)(self.map, link=link.link).get_item()
            if item:
                _load_image(item, 'adv')
                self.session.add(Advert(data=json.dumps(item), link=link.link))
            link.is_parsed = True
            self.session.commit()
