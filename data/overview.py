from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal

from utils.db import order_data_db, trade_data_db


def get_in_trading_orders_count(order_type: Literal["buy", "sell", "all"]) -> int:
    """获取交易中订单总数

    Args:
        order_type (Literal["buy", "sell", "all"]): 订单类型

    Returns:
        int: 交易中订单总数
    """
    filter: Dict[str, Any] = {
        "status": 0,  # 交易中
    }
    if order_type in {"buy", "sell"}:
        filter["order.type"] = order_type
    return order_data_db.count_documents(filter)


def get_finished_orders_count(order_type: Literal["buy", "sell", "all"]) -> int:
    """获取已完成订单总数

    Args:
        order_type (Literal["buy", "sell", "all"]): 订单类型

    Returns:
        int: 已完成订单总数
    """
    filter: Dict[str, Any] = {
        "status": 1,  # 已完成
    }
    if order_type in {"buy", "sell"}:
        filter["order.type"] = order_type
    return order_data_db.count_documents(filter)


def get_FTN_avagae_price(order_type: Literal["buy", "sell"]) -> float:
    """获取简书贝均价

    如果当前处于交易中的订单量少于 5 条，将视为数据不足，返回官方指导价 0.1

    Args:
        order_type (Literal["buy", "sell"]): 订单类型

    Returns:
        float: 简书贝均价
    """
    if get_in_trading_orders_count(order_type) < 5:
        return 0.1  # 数据不足，结果不准确，返回官方指导价

    return round(
        list(
            order_data_db.aggregate(
                [
                    {
                        "$match": {
                            "status": 0,  # 交易中
                            "order.type": order_type,
                        },
                    },
                    {
                        "$group": {
                            "_id": None,
                            "result": {
                                "$avg": "$order.price.unit",
                            },
                        },
                    },
                ]
            )
        )[0]["result"],
        3,
    )


def get_total_traded_amount() -> int:
    return list(
        trade_data_db.aggregate(
            [
                {
                    "$group": {
                        "_id": None,
                        "result": {
                            "$sum": "$trade_amount",
                        },
                    }
                },
            ]
        )
    )[0]["result"]


def get_total_traded_price() -> float:
    return list(
        trade_data_db.aggregate(
            [
                {
                    "$group": {
                        "_id": None,
                        "result": {
                            "$sum": "$total_price",
                        },
                    }
                },
            ]
        )
    )[0]["result"]


def get_24h_finish_orders_count(order_type: Literal["buy", "sell", "all"]) -> int:
    filter: Dict[str, Any] = {
        "finish_time": {
            "$gte": datetime.now() - timedelta(days=1),
        }
    }
    if order_type in {"buy", "sell"}:
        filter["order.type"] = order_type
    return order_data_db.count_documents(filter)


def get_24h_delete_orders_count(order_type: Literal["buy", "sell", "all"]) -> int:
    filter: Dict[str, Any] = {
        "delete_time": {
            "$gte": datetime.now() - timedelta(days=1),
        }
    }
    if order_type in {"buy", "sell"}:
        filter["order.type"] = order_type
    return order_data_db.count_documents(filter)


def get_24h_traded_FTN_amount(trade_type: Literal["buy", "sell"]) -> int:
    return list(
        trade_data_db.aggregate(
            [
                {
                    "$match": {
                        "trade_time": {
                            "$gte": datetime.now() - timedelta(days=1),
                        },
                        "trade_type": trade_type,
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "result": {
                            "$sum": "$trade_amount",
                        },
                    }
                },
            ]
        )
    )[0]["result"]


def get_24h_traded_FTN_total_price(trade_type: Literal["buy", "sell"]) -> float:
    return list(
        trade_data_db.aggregate(
            [
                {
                    "$match": {
                        "trade_time": {
                            "$gte": datetime.now() - timedelta(days=1),
                        },
                        "trade_type": trade_type,
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "result": {
                            "$sum": "$total_price",
                        },
                    }
                },
            ]
        )
    )[0]["result"]


def get_24h_traded_FTN_avg_price(trade_type: Literal["buy", "sell"]) -> float:
    return round(
        list(
            trade_data_db.aggregate(
                [
                    {
                        "$match": {
                            "trade_time": {
                                "$gte": datetime.now() - timedelta(days=1),
                            },
                            "trade_type": trade_type,
                        }
                    },
                    {
                        "$group": {
                            "_id": None,
                            "result": {
                                "$avg": "$unit_price",
                            },
                        }
                    },
                ]
            )
        )[0]["result"],
        3,
    )


def get_per_hour_trade_amount(
    trade_type: Literal["buy", "sell"], hours: int
) -> List[Dict]:
    return list(
        trade_data_db.aggregate(
            [
                {
                    "$match": {
                        "trade_time": {
                            "$gte": datetime.now() - timedelta(hours=hours),
                        },
                        "trade_type": trade_type,
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateTrunc": {
                                "date": "$trade_time",
                                "unit": "hour",
                            },
                        },
                        "traded_amount": {
                            "$sum": "$trade_amount",
                        },
                    }
                },
                {
                    "$sort": {
                        "_id": 1,
                    }
                },
            ]
        )
    )


def get_per_day_trade_amount(
    trade_type: Literal["buy", "sell"], days: int
) -> List[Dict]:
    return list(
        trade_data_db.aggregate(
            [
                {
                    "$match": {
                        "trade_time": {
                            "$gte": datetime.now() - timedelta(days=days),
                        },
                        "trade_type": trade_type,
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateTrunc": {
                                "date": "$trade_time",
                                "unit": "day",
                            },
                        },
                        "traded_amount": {
                            "$sum": "$trade_amount",
                        },
                    }
                },
                {
                    "$sort": {
                        "_id": 1,
                    },
                },
            ]
        )
    )


def get_per_hour_trade_avg_price(
    trade_type: Literal["buy", "sell"], hours: int
) -> List[Dict]:
    return list(
        trade_data_db.aggregate(
            [
                {
                    "$match": {
                        "trade_time": {
                            "$gte": datetime.now() - timedelta(hours=hours),
                        },
                        "trade_type": trade_type,
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateTrunc": {
                                "date": "$trade_time",
                                "unit": "hour",
                            },
                        },
                        "avg_price": {
                            "$avg": "$unit_price",
                        },
                    }
                },
                {
                    "$sort": {
                        "_id": 1,
                    },
                },
            ]
        )
    )


def get_per_day_trade_avg_price(
    trade_type: Literal["buy", "sell"], days: int
) -> List[Dict]:
    return list(
        trade_data_db.aggretgate(
            [
                {
                    "$match": {
                        "trade_time": {
                            "$gte": datetime.now() - timedelta(days=days),
                        },
                        "trade_type": trade_type,
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateTrunc": {
                                "date": "$trade_time",
                                "unit": "day",
                            },
                        },
                        "avg_price": {
                            "$avg": "$unit_price",
                        },
                    }
                },
                {
                    "$sort": {
                        "_id": 1,
                    },
                },
            ]
        )
    )
