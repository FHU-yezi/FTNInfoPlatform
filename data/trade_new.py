from datetime import datetime
from typing import Any, Dict, List, Literal, Sequence

from bson import ObjectId

from utils.db import trade_data_db
from utils.dict_helper import flatten_dict, get_reversed_dict
from utils.exceptions import (
    AmountIlliegalError,
    PriceIlliegalError,
    TradeNotExistError,
)
from utils.time_helper import get_now_without_mileseconds


class Trade:
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

    @property
    def object_id(self) -> ObjectId:
        return ObjectId(self.id)

    @classmethod
    def from_id(cls, id: str) -> "Trade":
        db_data = trade_data_db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise TradeNotExistError
        return cls.from_db_data(db_data)

    @classmethod
    def from_db_data(cls, db_data: Dict) -> "Trade":
        # 展平数据库查询结果
        db_data = flatten_dict(db_data)
        db_data["_id"] = str(db_data["_id"])

        data_to_init_func: Dict[str, Any] = {}
        for k, v in db_data.items():
            attr_name = cls.db_key_attr_mapping.get(k)
            if not attr_name:  # 数据库中存在，但模型中未定义的字段
                continue  # 跳过
            data_to_init_func[attr_name] = v

        # 调用 __init__ 初始化对象
        return cls(**data_to_init_func)

    def __setattr__(self, __name: str, __value: Any) -> None:
        # 由于脏属性列表在 __init__ 函数的末尾，当该列表存在时
        # 证明 __init__ 过程已完成
        init_finished: bool = hasattr(self, "_dirty")

        # __init__ 已完成，禁止设置模型中未定义的属性
        if init_finished and not hasattr(self, __name):
            raise Exception(f"不能设置模型中未定义的属性 {__name}")

        # 如果脏属性列表存在，且该属性未被标脏，则将该属性标脏
        if init_finished and __name not in self._dirty:
            self._dirty.append(__name)
        # 设置属性值
        super().__setattr__(__name, __value)

    def sync(self) -> None:
        data_to_update = {}
        # 遍历脏数据列表
        for attr in self._dirty:
            db_key: str = self.__class__.attr_db_key_mapping[attr]
            data_to_update[db_key] = getattr(self, attr)

        # 更新数据库中的信息
        trade_data_db.update_one({"_id": self.object_id}, {"$set": data_to_update})
        # 清空脏数据列表
        self._dirty.clear()

    def sync_only(self, attr_list: Sequence[str]) -> None:
        data_to_update = {}
        for attr in attr_list:
            if attr not in self._dirty:
                raise Exception(f"{attr} 未被标记为脏数据")
            db_key: str = self.__class__.attr_db_key_mapping[attr]
            data_to_update[db_key] = getattr(self, attr)

            # 从脏数据列表中删除对应属性名
            self._dirty.remove(attr)

        # 更新数据库中的信息
        trade_data_db.update_one({"_id": self.object_id}, {"$set": data_to_update})

    def sync_all(self) -> None:
        data_to_update = {}
        for attr, db_key in self.__class__.attr_db_key_mapping.items():
            data_to_update[db_key] = getattr(self, attr)

        # 更新数据库中的信息
        trade_data_db.update_one({"_id": self.object_id}, {"$set": data_to_update})
        # 清空脏数据列表
        self._dirty.clear()

    def remove(self) -> None:
        trade_data_db.delete_one({"_id": self.object_id})

    @property
    def order(self):
        from data.order_new import Order

        return Order.from_id(self.order_id)

    @property
    def user(self):
        from data.user_new import User

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
        insert_result = trade_data_db.insert_one(
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
