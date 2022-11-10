from typing import Optional

from pywebio.output import put_collapse, put_markdown, put_row

from data.order_new import Order
from data.user_new import User
from utils.html import link
from utils.page import is_Android
from utils.url_scheme import user_URL_to_URL_scheme
from widgets.badge import put_badge
from widgets.progress_bar import put_progress_bar


def put_order_item(order: Order, current_user: Optional[User] = None):
    # 受限于调用者，不能保证获取到当前用户对象
    # 如无法获取，传入默认值 None，使“我的”比较横为假
    order_user: User = order.user

    return put_collapse(
        title=f"单价 {order.unit_price} / 剩余 {order.remaining_amount} 个",
        content=[
            put_row(
                [
                    put_badge("我的", color="success")
                    if order_user == current_user
                    else put_markdown(""),
                    None,
                    put_badge("未绑定简书", color="warning")
                    if not order_user.is_jianshu_binded
                    else put_markdown(""),
                    None,
                ],
                size="auto 10px auto 1fr",
            ),
            put_markdown(
                f"""
                发布时间：{order.publish_time}
                发布者：{order.user_name}
                已交易 / 总量：{order.traded_amount} / {order.total_amount}
                """
            ),
            put_row(
                [
                    put_markdown("交易进度："),
                    put_progress_bar(order.traded_amount, order.total_amount),
                    None,
                    put_markdown(
                        f"{round(order.traded_amount / order.total_amount * 100)}%"
                    ),
                    None,
                ],
                size="auto auto 10px auto 1fr",
            ),
            put_markdown(
                "简书个人主页：" + link("点击跳转", order_user.jianshu_url, new_window=True)
                if order_user.is_jianshu_binded
                else "",
                sanitize=False,
            ),
            put_markdown(
                "一键跳转简书 App："
                + link(
                    "点击跳转",
                    user_URL_to_URL_scheme(order_user.jianshu_url),
                    new_window=False,
                )
                if order_user.is_jianshu_binded and is_Android()
                else "",
                sanitize=False,
            ),
        ],
    )


def put_order_detail(order: Order) -> None:
    put_markdown(
        f"""
        ## {'买单'if order.type == "buy" else '卖单'}

        发布时间：{order.publish_time}
        过期时间：{order.expire_time}
        单价：{order.unit_price}
        已交易 / 总量：{order.traded_amount} / {order.total_amount}
        剩余：{order.remaining_amount}
        总价：{order.total_price}
        """
    )
    put_row(
        [
            put_markdown("交易进度："),
            put_progress_bar(order.traded_amount, order.total_amount),
            None,
            put_markdown(f"{round(order.traded_amount / order.total_amount * 100)}%"),
            None,
        ],
        size="auto auto 10px auto 1fr",
    ),


def put_finished_order_item(order: Order) -> None:
    return put_collapse(
        title=f"成交于 {str(order.finish_time).split(' ')[0]} / 共 {order.total_price} 元",
        content=[
            put_markdown(
                f"""
                发布时间：{order.publish_time}
                单价：{order.unit_price}
                总量：{order.total_amount}
                """
            )
        ],
    )
