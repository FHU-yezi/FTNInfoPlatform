from pymongo import MongoClient, IndexModel

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
run_log_db = db.run_log
access_log_db = db.access_log

# 创建索引

order_data_db.create_indexes(
    [
        IndexModel([("status", 1)]),
        IndexModel([("order.type", 1)]),
        IndexModel([("user.id", 1)]),
        IndexModel([("order.price.unit", 1)]),
    ]
)

trade_data_db.create_indexes(
    [
        IndexModel([("trade_type", 1)]),
        IndexModel([("unit_price", 1)]),
        IndexModel([("order.id", 1)]),
        IndexModel([("user.id", 1)]),
    ]
)

user_data_db.create_indexes(
    [
        IndexModel([("user_name", 1)]),
        IndexModel([("jianshu.url", 1)]),
    ]
)
token_data_db.create_indexes(
    [
        IndexModel([("token", 1)]),
        # 过期索引
        IndexModel([("expire_time", 1)], expireAfterSeconds=0)
    ]
)
