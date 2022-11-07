from typing import Literal


class Trade:
    def __init__(self) -> None:
        pass

    @classmethod
    def create(
        cls,
        trade_type: Literal["buy", "sell"],
        unit_price: float,
        trade_amount: int,
        order_obj,
    ) -> "Trade":
        pass
