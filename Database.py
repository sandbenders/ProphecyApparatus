import pymongo

class Database():
    def __init__(self):
        super().__init__()
        self.client = pymongo.MongoClient()
        self.db = self.client.prophecy_apparatus

    def check_if_image_exists(self, to_search):
        return self.db.images.find_one({'_id': to_search})

    def insert_database(self, data_to_insert):
        self.db.images.insert_one(data_to_insert)

    def update_last_download(self, data_to_update):
        self.db.last_downloads.update_one({'_id': data_to_update['_id']}, {"$set": data_to_update}, upsert=True)

    def return_last_download(self, sub_reddit):
        last_download = self.db.last_downloads.find_one({'_id': sub_reddit})
        try:
            return last_download['before']
        except TypeError:
            return 0