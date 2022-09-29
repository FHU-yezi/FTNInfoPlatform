from utils.db import trade_data_db
from typing import Literal
from utils.time_helper import get_now_without_mileseconds
from utils.exceptions import PriceIlliegalError, AmountIlliegalError


def create_trade(
    order_id: str,
    trade_type: Literal["buy", "sell"],
    unit_price: float,
    trade_amount: int,
    uid: str,
) -> None:
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
    trade_data_db.insert_one(
        {
            "trade_time": get_now_without_mileseconds(),
            "trade_type": trade_type,
            "unit_price": unit_price,
            "trade_amount": trade_amount,
            "total_price": total_price,
            "order": {
                "id": order_id,
            },
            "user": {
                "id": uid,
            },
        }
    )
