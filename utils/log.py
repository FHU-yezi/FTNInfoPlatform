from datetime import datetime
from typing import Optional

from utils.db import access_log_db


class AccessLogger():
    def __init__(self, db) -> None:
        self._db = db

    def log(self, module: str, ua: str, ip: str, protocol: str, cookie: str) -> None:
        self._db.insert_one({
            "time": datetime.now(),
            "module": module,
            "ua": ua,
            "ip": ip,
            "protocol": protocol,
            "cookie": cookie
        })

    def log_from_info_obj(self, module_name: str, info_obj, cookie: Optional[str]) -> None:
        self.log(
            module=module_name,
            ua=info_obj.user_agent.ua_string,
            ip=info_obj.user_ip,
            protocol=info_obj.protocol,
            cookie=cookie
        )


access_logger: AccessLogger = AccessLogger(
    db=access_log_db
)