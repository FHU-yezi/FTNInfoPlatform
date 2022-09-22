from pymongo import MongoClient

from utils.config import config


def init_DB(db_name: str):
    connection: MongoClient = MongoClient(config.db.host, config.db.port)
    db = connection[db_name]
    return db


db = init_DB(config.db.main_database)


def get_collection(collection_name: str):
    return db[collection_name]


trade_data_db = db.trade_data
user_data_db = db.user_data
cookie_data_db = db.cookie_data
access_log_db = db.access_log


# 如果索引不存在，创建对应索引
if not trade_data_db.list_indexes():
    pass
if not user_data_db.list_indexes():
    pass
if not cookie_data_db.list_indexes():
    # 在 expire_time 时间点过期
    cookie_data_db.create_index([("expire_time", 1)], expireAfterSeconds=0)