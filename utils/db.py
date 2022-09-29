from pymongo import MongoClient

from utils.config import config


def init_DB(db_name: str):
    connection: MongoClient = MongoClient(config.db.host, config.db.port)
    db = connection[db_name]
    return db


db = init_DB(config.db.main_database)


def get_collection(collection_name: str):
    return db[collection_name]


order_data_db = db.order_data
trade_data_db = db.trade_data
user_data_db = db.user_data
token_data_db = db.token_data
access_log_db = db.access_log

# 创建索引

order_data_db.create_index([("status", 1)])
order_data_db.create_index([("order.type", 1)])
order_data_db.create_index([("user.id", 1)])
order_data_db.create_index([("order.price.unit", 1)])

trade_data_db.create_index([("trade_type", 1)])
trade_data_db.create_index([("unit_price", 1)])
trade_data_db.create_index([("order.id", 1)])
trade_data_db.create_index([("user.id", 1)])

token_data_db.create_index([("token", 1)])

# 在 expire_time 时间点过期
token_data_db.create_index([("expire_time", 1)], expireAfterSeconds=0)
