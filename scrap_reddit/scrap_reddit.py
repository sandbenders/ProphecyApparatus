import sys
import json
import urllib.error
import argparse

from datetime import datetime as dt
from urllib.request import urlopen, urlretrieve
from threading import Thread

from cuter import *

sys.path.append('..')
from Database import *


class DownloadImage:
    def __init__(self, image_info):
        self.id = image_info['id']
        self.image_path = '/hologram/datasets/prophecy_apparatus/originals/{}.jpg'.format(self.id)
        self.cropped_image_path = self.image_path.replace('originals', 'cropped')
        self.url = image_info['url']
        self.author = image_info['author']
        self.sub_reddit = image_info['subreddit']
        self.before = image_info['before']

    def download_image(self):
        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent',
                                  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(self.url, self.image_path)
            print('Downloaded: {}'.format(self.url))
            self.add_to_database()
        except urllib.error.URLError as e:
            print('Error {} downloading {}'.format(e, self.url))
        except ConnectionResetError as e:
            print('Error {} downloading {}'.format(e, self.url))
        except UnicodeEncodeError as e:
            print('Error {} downloading {}'.format(e, self.url))

    def add_to_database(self):
        data_to_insert = {}
        data_to_insert['_id'] = self.id
        data_to_insert['sub_reddit'] = self.sub_reddit
        data_to_insert['url'] = self.url
        data_to_insert['author'] = self.author
        data_to_insert['date'] = dt.today()
        database = Database()
        database.insert_database(data_to_insert)

        data_to_update = {}
        data_to_update['_id'] = self.sub_reddit
        data_to_update['date'] = dt.today()
        data_to_update['before'] = self.before
        database = Database()
        database.update_last_download(data_to_update)

        resize_and_crop(self.image_path, self.cropped_image_path, (1080, 1920), 'middle')


class ScrapReddit:
    def __init__(self, sub_reddit, position):
        database = Database()
        self.sub_reddit = sub_reddit
        self.before = database.return_last_download(self.sub_reddit) if position else 0
        print(self.before)
        self.URL = 'https://api.pushshift.io/reddit/submission/search/?subreddit={}&sort=desc&size=1000'.format(
            self.sub_reddit)
        self.scrap()

    def scrap(self):
        while True:
            try:
                url_to_open = self.URL + '&before={}d&after={}d'.format(self.before, self.before + 1)
                url = urlopen(url_to_open)
                responses = json.loads(url.read())
                if len(responses['data']) > 0:
                    for resp in responses['data']:
                        database = Database()
                        if not database.check_if_image_exists(resp['id']) and '.jpg' in resp['url']:
                            resp['before'] = self.before
                            download_image = DownloadImage(resp)
                            t = Thread(target=download_image.download_image())
                            t.start()
                self.before += 1
            except urllib.error.HTTPError as e:
                print('Error {}'.format(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrap images from subreddits')
    parser.add_argument('-s', '--subreddit',
                        dest='subreddit',
                        action='store',
                        default='futureporn',
                        help='subreddit to scrap')
    parser.add_argument('-p', '--position',
                        dest='position',
                        action='store_true',
                        help='take the former position')
    args = parser.parse_args()

    scrap_reddit = ScrapReddit(args.subreddit, args.position)
