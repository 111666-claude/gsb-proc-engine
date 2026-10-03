"""触发引擎：事件订阅索引、内部冷却、触发上限与事件幂等。"""


class Engine:
    """触发（proc）引擎。"""

    def __init__(self):
        self.procs = {}
        self.state = {}
        self.subscribers = {}
        self.handled = set()
        self.scanned = 0

    def register(self, proc_id, event, icd_ms=0, max_triggers=0):
        if proc_id in self.procs:
            old_event = self.procs[proc_id]["event"]
            bucket = self.subscribers.get(old_event)
            if bucket is not None:
                bucket.pop(proc_id, None)
        self.procs[proc_id] = {"id": proc_id, "event": event, "icd_ms": icd_ms,
                               "max_triggers": max_triggers}
        self.state.setdefault(proc_id, {"last": None, "count": 0})
        self.subscribers.setdefault(event, {})[proc_id] = None

    def fire(self, event, now_ms, event_id, roll=0):
        """派发一次事件，返回被触发的 proc 列表。"""
        if event_id in self.handled:
            return []
        self.handled.add(event_id)

        out = []
        for proc_id in self.subscribers.get(event, ()):
            self.scanned += 1
            proc = self.procs[proc_id]
            st = self.state[proc_id]

            max_triggers = proc["max_triggers"]
            if max_triggers > 0 and st["count"] >= max_triggers:
                continue

            icd_ms = proc["icd_ms"]
            if st["last"] is not None and now_ms - st["last"] < icd_ms:
                continue

            out.append(proc_id)
            st["count"] += 1
            st["last"] = now_ms
        return out

    def triggers(self, proc_id):
        return self.state.get(proc_id, {}).get("count", 0)

    def scanned_count(self):
        return self.scanned
