from typing import Dict, List, Literal

from bson import ObjectId
from data.user import get_user_data_from_uid
from utils.db import order_data_db
from utils.exceptions import (
    AmountIlliegalError,
    DuplicatedOrderError,
    OrderIDNotExistError,
    OrderStatusError,
    PriceIlliegalError,
)
from utils.time_helper import get_now_without_mileseconds


def is_order_id_exist(order_id: str) -> bool:
    """检测意向单 ID 是否存在

    Args:
        order_id (str): 订单 ID

    Returns:
        bool: 是否存在
    """
    return order_data_db.count_documents({"_id": ObjectId(order_id)}) != 0


def is_uid_order_type_exist(uid: str, order_type: Literal["buy", "sell"]) -> bool:
    """检测某用户是否已发布过该种交易单

    Args:
        uid (str): UID
        order_type (Literal["buy", "sell"]): 订单类型

    Returns:
        bool: 是否已发布过该种交易单
    """
    return (
        order_data_db.count_documents(
            {
                "status": 0,  # 交易中
                "order.type": order_type,
                "user.id": uid,
            }
        )
    ) != 0


def get_order_data_from_order_id(order_id: str) -> Dict:
    """通过订单 ID 获取订单信息

    Args:
        order_id (str): 订单 ID

    Raises:
        OrderIDNotExistError: 订单不存在

    Returns:
        Dict: 订单信息
    """
    result: Dict = order_data_db.find_one({"_id": ObjectId(order_id)})
    if not result:
        raise OrderIDNotExistError("Order ID 不存在")
    return result


def create_order(
    order_type: Literal["buy", "sell"], unit_price: float, total_amount: int, uid: str
):
    """创建订单

    Args:
        order_type (Literal["buy", "sell"]): 订单类型
        unit_price (float): 单价
        total_amount (int): 总量
        uid (str): UID

    Raises:
        TypeError: 参数 order_type 错误（内部错误）
        PriceIlliegalError: 价格为空或不在正常范围内
        AmountIlliegalError: 总量为空或不在正常范围内
        DuplicatedOrderError: 该用户已存在对应类型交易单，不允许重复创建
    """
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

    if is_uid_order_type_exist(uid, order_type):
        raise DuplicatedOrderError("该用户已存在该类型交易单")

    total_price = round(unit_price * total_amount, 2)
    # 此处如果 UID 不存在，会抛出异常
    # 但调用方有责任保证 UID 存在，这是一个内部异常，因此不做捕获处理
    user_data = get_user_data_from_uid(uid)
    order_data_db.insert_one(
        {
            "publish_time": get_now_without_mileseconds(),
            "finish_time": None,
            "delete_time": None,
            "status": 0,
            "order": {
                "type": order_type,
                "price": {"unit": unit_price, "total": total_price},
                "amount": {
                    "total": total_amount,
                    "traded": 0,
                    "remaining": total_amount,
                },
            },
            "user": {
                "id": uid,
                "name": user_data["user_name"],
            },
        }
    )


def change_order_unit_price(order_id: str, unit_price: float) -> None:
    """更改订单单价

    Args:
        order_id (str): 订单 ID
        unit_price (float): 新单价

    Raises:
        PriceIlliegalError: 单价为空或不在正常范围内
    """
    if unit_price is None:
        raise PriceIlliegalError("单价不能为空")
    if not 0.05 < unit_price <= 0.2:
        raise PriceIlliegalError("单价必须在 0.05 - 0.2 之间")
    if round(unit_price, 3) != unit_price:  # 大于三位小数
        raise PriceIlliegalError("价格只支持三位小数")

    # 此处如果 Order ID 不存在，会抛出异常
    # 但调用方有责任保证 Order ID 存在，这是一个内部异常，因此不做捕获处理
    order_data = get_order_data_from_order_id(order_id)
    total_price: float = round(unit_price * order_data["order"]["amount"]["total"], 2)

    data_to_update: Dict = {
        "order.price": {
            "unit": unit_price,
            "total": total_price,
        },
    }
    order_data_db.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": data_to_update},
    )


def change_order_traded_amount(order_id: str, traded_amount: int) -> None:
    """更改订单已交易数量

    该函数不会阻止用户将已交易数量更改为比现有值更低的数值

    Args:
        order_id (str): 订单 ID
        traded_amount (int): 已交易数量

    Raises:
        AmountIlliegalError: 已交易量为空或不在正常范围内
    """
    if traded_amount is None:
        raise AmountIlliegalError("已交易量不能为空")
    if traded_amount < 0:
        raise AmountIlliegalError("已交易量必须大于 0")

    # 此处如果 Order ID 不存在，会抛出异常
    # 但调用方有责任保证 Order ID 存在，这是一个内部异常，因此不做捕获处理
    order_data = get_order_data_from_order_id(order_id)
    total_amount: int = order_data["order"]["amount"]["total"]
    if traded_amount > total_amount:
        raise AmountIlliegalError("已交易量不能大于总量")

    remaining_amount: int = total_amount - traded_amount
    unit_price: float = order_data["order"]["price"]["unit"]
    total_price: float = round(unit_price * total_amount, 2)

    data_to_update: Dict = {
        "order.price": {
            "unit": unit_price,
            "total": total_price,
        },
        "order.amount": {
            "total": total_amount,
            "traded": traded_amount,
            "remaining": remaining_amount,
        },
    }
    # 如果余量为 0，将交易单状态置为已完成
    if remaining_amount == 0:
        data_to_update["status"] = 1  # 已完成
        data_to_update["finish_time"] = get_now_without_mileseconds()
    order_data_db.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": data_to_update},
    )


def delete_order(order_id: str) -> None:
    """删除订单

    Args:
        order_id (str): 订单 ID

    Raises:
        OrderStatusError: 订单不存在
    """
    # 此处如果 Order ID 不存在，会抛出异常
    # 但调用方有责任保证 Order ID 存在，这是一个内部异常，因此不做捕获处理
    order_data = get_order_data_from_order_id(order_id)

    if order_data["status"] != 0:
        raise OrderStatusError("不能对状态不为交易中的交易单进行删除操作")

    # 将交易单标记为已删除
    data_to_update: Dict = {
        "status": 2,  # 已删除
        "delete_time": get_now_without_mileseconds(),
    }
    order_data_db.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": data_to_update},
    )


def get_active_orders_list(
    order_type: Literal["buy", "sell"], limit: int
) -> List[Dict]:
    """获取交易中的订单列表

    Args:
        order_type (Literal["buy", "sell"]): 订单类型
        limit (int): 返回数量限制

    Returns:
        List[Dict]: 订单列表
    """
    return (
        order_data_db.find(
            {
                "status": 0,  # 交易中
                "order.type": order_type,
            }
        )
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


def get_my_active_order(uid: str, order_type: Literal["buy", "sell"]) -> Dict:
    """获取自己的交易中订单

    Args:
        uid (str): UID
        order_type (Literal["buy", "sell"]): 订单类型

    Returns:
        Dict: 订单信息
    """
    return order_data_db.find_one(
        {
            "status": 0,  # 交易中
            "order.type": order_type,
            "user.id": uid,
        }
    )


def get_my_finished_orders_list(
    uid: str, order_type: Literal["buy", "sell"]
) -> List[Dict]:
    """获取自己的已完成订单

    Args:
        uid (str): UID
        order_type (Literal["buy", "sell"]): 订单类型

    Returns:
        List[Dict]: 订单信息
    """
    return order_data_db.find(
        {
            "status": 1,  # 已完成
            "order.type": order_type,
            "user.id": uid,
        }
    )
