from datetime import datetime
from typing import Dict, List, Literal

from bson import ObjectId

from data._base import DataModel
from utils.db import trade_data_db
from utils.dict_helper import get_reversed_dict
from utils.exceptions import (
    AmountIlliegalError,
    PriceIlliegalError,
    TradeNotExistError,
)
from utils.time_helper import get_now_without_mileseconds


class Trade(DataModel):
    db = trade_data_db
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "trade_time": "trade_time",
        "type": "trade_type",
        "unit_price": "unit_price",
        "trade_amount": "trade_amount",
        "total_price": "total_price",
        "order_id": "order.id",
        "user_id": "user.id",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(
        self,
        id: str,
        trade_time: datetime,
        type: Literal["buy", "sell"],
        unit_price: float,
        trade_amount: int,
        total_price: float,
        order_id: str,
        user_id: str,
    ) -> None:
        self.id = id
        self.trade_time = trade_time
        # 此处覆盖了内置函数 type，该作用域内不会使用到这个函数
        self.type = type
        self.unit_price = unit_price
        self.trade_amount = trade_amount
        self.total_price = total_price
        self.order_id = order_id
        self.user_id = user_id

        # 脏属性列表必须在其它属性设置后再被创建
        self._dirty: List[str] = []

    @classmethod
    def from_id(cls, id: str) -> "Trade":
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise TradeNotExistError
        return cls.from_db_data(db_data)

    @property
    def order(self):
        from data.order import Order

        return Order.from_id(self.order_id)

    @property
    def user(self):
        from data.user import User

        return User.from_id(self.user_id)

    @classmethod
    def create(
        cls,
        trade_type: Literal["buy", "sell"],
        unit_price: float,
        trade_amount: int,
        order_obj,
    ) -> "Trade":
        # 调用方有责任保证 Order ID 和 UID 存在，此函数不会进行校验
        if trade_type not in {"buy", "sell"}:
            raise TypeError("参数 order_type 必须为 buy 或 sell")
        if unit_price is None:
            raise PriceIlliegalError("单价不能为空")
        if trade_amount is None:
            raise AmountIlliegalError("交易量不能为空")
        if not 0.05 < unit_price <= 0.2:
            raise PriceIlliegalError("单价必须在 0.05 - 0.2 之间")

        total_price: float = round(unit_price * trade_amount, 2)
        insert_result = cls.db.insert_one(
            {
                "trade_time": get_now_without_mileseconds(),
                "trade_type": trade_type,
                "unit_price": unit_price,
                "trade_amount": trade_amount,
                "total_price": total_price,
                "order": {
                    "id": order_obj.id,
                },
                "user": {
                    "id": order_obj.user_id,
                },
            }
        )

        # 返回新创建的交易对象
        return cls.from_id(insert_result.inserted_id)
