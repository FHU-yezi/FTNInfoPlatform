from datetime import datetime
from typing import Any, Dict, List, Literal, Sequence

from bson import ObjectId

from utils.config import config
from utils.db import order_data_db
from utils.dict_helper import flatten_dict, get_reversed_dict
from utils.exceptions import (
    AmountIlliegalError,
    DuplicatedOrderError,
    OrderIDNotExistError,
    OrderStatusError,
    PriceIlliegalError,
)
from utils.time_helper import (
    get_nearest_expire_time,
    get_now_without_mileseconds,
)


def get_active_orders_list(
    order_type: Literal["buy", "sell", "all"], limit: int
) -> List[Dict]:
    """获取交易中的订单列表

    Args:
        order_type (Literal["buy", "sell", "all"]): 订单类型
        limit (int): 返回数量限制

    Returns:
        List[Dict]: 订单列表
    """
    filter: Dict[str, Any] = {"status": 0}  # 交易中
    if order_type in {"buy", "sell"}:
        filter["order.type"] = order_type

    return (
        order_data_db.find(filter)
        # 根据交易单类型应用对应排序规则
        # 买单价格升序，卖单价格降序
        .sort(
            [
                (
                    "order.price.unit",
                    -1 if order_type == "buy" else 1,
                )
            ]
        ).limit(limit)
    )


class Order:
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "status": "status",
        "type": "order.type",
        "publish_time": "publish_time",
        "finish_time": "finish_time",
        "delete_time": "delete_time",
        "effective_hours": "effective_hours",
        "expire_time": "expire_time",
        "unit_price": "order.price.unit",
        "total_price": "order.price.total",
        "total_amount": "order.amount.total",
        "traded_amount": "order.amount.traded",
        "remaining_amount": "order.amount.remaining",
        "user_id": "user.id",
        "user_name": "user.name",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(
        self,
        id: str,
        status: int,
        type: str,
        publish_time: datetime,
        finish_time: datetime,
        delete_time: datetime,
        effective_hours: int,
        expire_time: datetime,
        unit_price: float,
        total_price: float,
        total_amount: int,
        traded_amount: int,
        remaining_amount: int,
        user_id: str,
        user_name: str,
    ) -> None:
        self.id = id
        self.status = status
        # 此处覆盖了内置函数 type，该作用域内不会使用到这个函数
        self.type = type
        self.publish_time = publish_time
        self.finish_time = finish_time
        self.delete_time = delete_time
        self.effective_hours = effective_hours
        self.expire_time = expire_time
        self.unit_price = unit_price
        self.total_price = total_price
        self.total_amount = total_amount
        self.traded_amount = traded_amount
        self.remaining_amount = remaining_amount
        self.user_id = user_id
        self.user_name = user_name

        # 脏属性列表必须在其它属性设置后再被创建
        self._dirty: List[str] = []

    @property
    def object_id(self) -> ObjectId:
        return ObjectId(self.id)

    @classmethod
    def from_id(cls, id: str) -> "Order":
        db_data = order_data_db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise OrderIDNotExistError
        return cls.from_db_data(db_data)

    @classmethod
    def from_db_data(cls, db_data: Dict) -> "Order":
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

    def __eq__(self, __o: Any) -> bool:
        if self.__class__ != __o.__class__:
            return False

        return self.id == __o.id

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
        order_data_db.update_one({"_id": self.object_id}, {"$set": data_to_update})
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
        order_data_db.update_one({"_id": self.object_id}, {"$set": data_to_update})

    def sync_all(self) -> None:
        data_to_update = {}
        for attr, db_key in self.__class__.attr_db_key_mapping.items():
            data_to_update[db_key] = getattr(self, attr)

        # 更新数据库中的信息
        order_data_db.update_one({"_id": self.object_id}, {"$set": data_to_update})
        # 清空脏数据列表
        self._dirty.clear()

    def remove(self) -> None:
        order_data_db.delete_one({"_id": self.object_id})

    @property
    def user(self):
        from data.user_new import User

        return User.from_id(self.user_id)

    @property
    def trade_list(self):
        from data.trade_new import Trade
        from utils.db import trade_data_db

        db_data_list: List[Dict] = trade_data_db.find(
            {"order.id": self.id},
        )
        return [Trade.from_db_data(item) for item in db_data_list]

    @classmethod
    def create(
        cls,
        order_type: Literal["buy", "sell"],
        unit_price: float,
        total_amount: int,
        user_obj,
    ) -> "Order":
        if order_type not in {"buy", "sell"}:
            raise TypeError("参数 order_type 必须为 buy 或 sell")
        if unit_price is None:
            raise PriceIlliegalError("单价不能为空")
        if total_amount is None:
            raise AmountIlliegalError("总量不能为空")

        if not 0.05 < unit_price <= 0.2:
            raise PriceIlliegalError("单价必须在 0.05 - 0.2 之间")
        if not 0 < total_amount <= 10**8:
            raise AmountIlliegalError("总量必须在 0 - 10**8 之间")
        if round(unit_price, 3) != unit_price:  # 大于三位小数
            raise PriceIlliegalError("价格只支持三位小数")

        # 该用户已经有同种交易单
        # user_obj 的 buy_order 和 sell_order 属性在没有交易单时返回 None
        if (order_type == "buy" and user_obj.buy_order) or (
            order_type == "sell" and user_obj.sell_order
        ):
            raise DuplicatedOrderError("该用户已存在该类型交易单")

        total_price = round(unit_price * total_amount, 2)
        now_time = get_now_without_mileseconds()
        insert_result = order_data_db.insert_one(
            {
                "publish_time": now_time,
                "effective_hours": config.default_order_effective_hours,
                "expire_time": get_nearest_expire_time(
                    now_time, config.default_order_effective_hours
                ),
                "finish_time": None,
                "delete_time": None,
                "status": 0,
                "order": {
                    "type": order_type,
                    "price": {
                        "unit": unit_price,
                        "total": total_price,
                    },
                    "amount": {
                        "total": total_amount,
                        "traded": 0,
                        "remaining": total_amount,
                    },
                },
                "user": {
                    "id": user_obj.id,
                    "name": user_obj.name,
                },
            }
        )

        # 返回新创建的订单对象
        return cls.from_id(insert_result.inserted_id)

    def change_unit_price(self, new_unit_price: float) -> None:
        if new_unit_price is None:
            raise PriceIlliegalError("单价不能为空")
        if not 0.05 < new_unit_price <= 0.2:
            raise PriceIlliegalError("单价必须在 0.05 - 0.2 之间")
        if round(new_unit_price, 3) != new_unit_price:  # 大于三位小数
            raise PriceIlliegalError("价格只支持三位小数")

        total_price: float = round(new_unit_price * self.total_amount, 2)

        self.unit_price = new_unit_price
        self.total_price = total_price
        self.sync()

    def change_traded_amount(self, new_traded_amount: int) -> None:
        if new_traded_amount is None:
            raise AmountIlliegalError("已交易量不能为空")
        if new_traded_amount < 0:
            raise AmountIlliegalError("已交易量必须大于 0")

        origin_traded_amount = self.traded_amount
        trade_amount = new_traded_amount - origin_traded_amount
        if new_traded_amount > self.total_amount:
            raise AmountIlliegalError("已交易量不能大于总量")
        if trade_amount <= 0:
            raise AmountIlliegalError("不能将已交易量改为低于当前值的数值")

        new_remaining_amount: int = self.total_amount - new_traded_amount

        # 更新订单状态
        self.traded_amount = new_traded_amount
        self.remaining_amount = new_remaining_amount
        # 创建交易
        from data.trade_new import Trade

        Trade.create(
            trade_type=self.type,
            unit_price=self.unit_price,
            trade_amount=trade_amount,
            order_obj=self,
        )
        # 如果余量为 0，将交易单状态置为已完成
        if new_remaining_amount == 0:
            self.status = 1  # 已完成
            self.finish_time = get_now_without_mileseconds()

        self.sync()

    def set_all_traded(self) -> None:
        # 将已交易数量设为订单总量，即全部简书贝都已被交易
        # 之后交由 `change_traded_amount` 函数处理
        return self.change_traded_amount(self.total_amount)

    def delete(self) -> None:
        order_data_db.delete_one({"_id": self.object_id})

    def expire(self) -> None:
        if self.status != 0:
            raise OrderStatusError("不能对状态不为交易中的交易单进行过期操作")

        self.status = 3  # 已过期
        self.expire_time = get_now_without_mileseconds()
        self.sync()
