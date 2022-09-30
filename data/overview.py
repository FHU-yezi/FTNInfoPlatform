from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Union

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


def get_24h_trade_count(trade_type: Literal["buy", "sell", "all"]) -> int:
    filter: Dict[str, Any] = {}
    if trade_type in {"buy", "sell"}:
        filter["trade_type"] = trade_type
    return trade_data_db.count_documents(filter)


def get_total_traded_amount() -> int:
    result = list(
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
    )
    if not result:
        return 0
    return result[0]["result"]


def get_total_traded_price() -> float:
    result = list(
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
    )
    if not result:
        return 0.0
    return result[0]["result"]


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
    filter: Dict[str, Any] = {
        "trade_time": {
            "$gte": datetime.now() - timedelta(days=1),
        },
    }
    if trade_type in {"buy", "sell"}:
        filter["trade_type"] = trade_type
    return list(
        trade_data_db.aggregate(
            [
                {
                    "$match": filter
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


def get_24h_traded_FTN_avg_price(trade_type: Literal["buy", "sell", "all"], missing: Literal["default", "ignore"]) -> Union[float, str]:
    if get_24h_trade_count(trade_type) < 5:
        if missing == "default":
            return 0.1  # 返回官方指导价
        else:
            return "-"

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
