"""触发引擎：事件订阅索引、内部冷却、触发上限与事件幂等。

缺陷：不按事件过滤、内部冷却不生效、触发上限不生效、同一个 event_id 重复触发、
每次派发扫描全部注册项。
"""


class Engine:
    """触发（proc）引擎。"""

    def __init__(self):
        self.procs = {}
        self.state = {}
        self.handled = set()
        self.scanned = 0

    def register(self, proc_id, event, icd_ms=0, max_triggers=0):
        self.procs[proc_id] = {"id": proc_id, "event": event, "icd_ms": icd_ms,
                               "max_triggers": max_triggers}
        self.state[proc_id] = {"last": None, "count": 0}

    def fire(self, event, now_ms, event_id, roll=0):
        """派发一次事件，返回被触发的 proc 列表。"""
        self.scanned += len(self.procs)
        self.handled.add(event_id)
        out = []
        for proc_id in self.procs:
            out.append(proc_id)
            self.state[proc_id]["count"] += 1
            self.state[proc_id]["last"] = now_ms
        return out

    def triggers(self, proc_id):
        return self.state.get(proc_id, {}).get("count", 0)

    def scanned_count(self):
        return self.scanned
