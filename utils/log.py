from datetime import datetime
from queue import Queue
from threading import Thread
from time import sleep
from typing import Dict, List, Optional

from utils.db import access_log_db


class AccessLogger:
    def __init__(self, db, save_interval: int) -> None:
        self._db = db
        self._save_interval = save_interval
        self._data_queue: Queue = Queue()
        self._save_thread = Thread(target=self._save_to_db)

        self._save_thread.start()

    def log(
        self, module: str, ua: str, ip: str, protocol: str, token: Optional[str]
    ) -> None:
        self._data_queue.put(
            {
                "time": datetime.now(),
                "module": module,
                "ua": ua,
                "ip": ip,
                "protocol": protocol,
                "token": token,
            }
        )

    def log_from_info_obj(
        self, module_name: str, info_obj, token: Optional[str]
    ) -> None:
        self.log(
            module=module_name,
            ua=info_obj.user_agent.ua_string,
            ip=info_obj.user_ip,
            protocol=info_obj.protocol,
            token=token,
        )

    def _save_to_db(self):
        while True:
            if not self._data_queue.empty():
                data_to_save: List[Dict] = []
                while not self._data_queue.empty():
                    data_to_save.append(self._data_queue.get())
                self._db.insert_many(data_to_save)
                data_to_save.clear()
            sleep(self._save_interval)

    def force_refresh(self):
        if self._data_queue.empty():  # 没有要保存的数据
            return
        data_to_save: List[Dict] = []
        while not self._data_queue.empty():
            data_to_save.append(self._data_queue.get())
        self._db.insert_many(data_to_save)


access_logger: AccessLogger = AccessLogger(
    db=access_log_db,
    save_interval=30,
)
