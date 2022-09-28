from datetime import datetime, timedelta
from typing import Dict, List, Literal

from utils.db import order_data_db


def get_active_orders_count() -> int:
    return order_data_db.count_documents(
        {
            "status": 0,  # 交易中
        }
    )


def get_finished_orders_count() -> int:
    return order_data_db.count_documents(
        {
            "status": 1,  # 已完成
        }
    )


def get_total_traded_amount() -> int:
    return list(
        order_data_db.aggregate(
            [
                {
                    "$match": {
                        "status": 1,  # 已完成
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "result": {
                            "$sum": "$order.amount.total",
                        },
                    }
                },
            ]
        )
    )[0]["result"]


def get_total_traded_price() -> float:
    return list(
        order_data_db.aggregate(
            [
                {
                    "$match": {
                        "status": 1,  # 已完成
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "result": {
                            "$sum": "$order.price.total",
                        },
                    }
                },
            ]
        )
    )[0]["result"]


def get_24h_finish_orders_count(order_type: Literal["buy", "sell"]) -> int:
    return order_data_db.count_documents(
        {
            "finish_time": {
                "$gte": datetime.now() - timedelta(days=1),
            },
            "order.type": order_type,
        }
    )


def get_24h_delete_orders_count(order_type: Literal["buy", "sell"]) -> int:
    return order_data_db.count_documents(
        {
            "delete_time": {
                "$gte": datetime.now() - timedelta(days=1),
            },
            "order.type": order_type,
        }
    )


def get_24h_traded_FTN_amount(order_type: Literal["buy", "sell"]) -> int:
    return list(
        order_data_db.aggregate(
            [
                {
                    "$match": {
                        "finish_time": {
                            "$gte": datetime.now() - timedelta(days=1),
                        },
                        "order.type": order_type,
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "result": {
                            "$sum": "$order.amount.total",
                        },
                    }
                },
            ]
        )
    )[0]["result"]


def get_24h_traded_FTN_total_price(order_type: Literal["buy", "sell"]) -> float:
    return list(
        order_data_db.aggregate(
            [
                {
                    "$match": {
                        "finish_time": {
                            "$gte": datetime.now() - timedelta(days=1),
                        },
                        "order.type": order_type,
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "result": {
                            "$sum": "$order.price.total",
                        },
                    }
                },
            ]
        )
    )[0]["result"]


def get_24h_traded_FTN_avg_price(order_type: Literal["buy", "sell"]) -> float:
    return round(
        list(
            order_data_db.aggregate(
                [
                    {
                        "$match": {
                            "finish_time": {
                                "$gte": datetime.now() - timedelta(days=1),
                            },
                            "order.type": order_type,
                        }
                    },
                    {
                        "$group": {
                            "_id": None,
                            "result": {
                                "$avg": "$order.price.unit",
                            },
                        }
                    },
                ]
            )
        )[0]["result"],
        3,
    )


def get_per_hour_traded_amount(
    order_type: Literal["buy", "sell"], hours: int
) -> List[Dict]:
    return list(
        order_data_db.aggregate(
            [
                {
                    "$match": {
                        "finish_time": {
                            "$gte": datetime.now() - timedelta(hours=hours),
                        },
                        "order.type": order_type,
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateTrunc": {
                                "date": "$finish_time",
                                "unit": "hour",
                            },
                        },
                        "traded_amount": {
                            "$sum": "$order.amount.total",
                        },
                    }
                },
                {"$sort": {"_id": 1}},
            ]
        )
    )


def get_per_day_traded_amount(
    order_type: Literal["buy", "sell"], days: int
) -> List[Dict]:
    return list(
        order_data_db.aggregate(
            [
                {
                    "$match": {
                        "finish_time": {
                            "$gte": datetime.now() - timedelta(days=days),
                        },
                        "order.type": order_type,
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateTrunc": {
                                "date": "$finish_time",
                                "unit": "day",
                            },
                        },
                        "traded_amount": {
                            "$sum": "$order.amount.total",
                        },
                    }
                },
                {"$sort": {"_id": 1}},
            ]
        )
    )


def get_per_hour_trade_avg_price(
    order_type: Literal["buy", "sell"], hours: int
) -> List[Dict]:
    return list(
        order_data_db.aggregate(
            [
                {
                    "$match": {
                        "finish_time": {
                            "$gte": datetime.now() - timedelta(hours=hours),
                        },
                        "order.type": order_type,
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateTrunc": {
                                "date": "$finish_time",
                                "unit": "hour",
                            },
                        },
                        "avg_price": {
                            "$avg": "$order.price.unit",
                        },
                    }
                },
                {"$sort": {"_id": 1}},
            ]
        )
    )


def get_per_day_trade_avg_price(
    order_type: Literal["buy", "sell"], days: int
) -> List[Dict]:
    return list(
        order_data_db.aggregate(
            [
                {
                    "$match": {
                        "finish_time": {
                            "$gte": datetime.now() - timedelta(days=days),
                        },
                        "order.type": order_type,
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateTrunc": {
                                "date": "$finish_time",
                                "unit": "day",
                            },
                        },
                        "avg_price": {
                            "$avg": "$order.price.unit",
                        },
                    }
                },
                {"$sort": {"_id": 1}},
            ]
        )
    )
