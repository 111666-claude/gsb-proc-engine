"""触发引擎：事件订阅索引、内部冷却、触发上限与事件幂等。"""


class Engine:
    """触发（proc）引擎。"""

    def __init__(self):
        self.procs = {}
        self.state = {}
        self.handled = set()
        self.scanned = 0
        self._by_event = {}
        self._sorted = {}

    def register(self, proc_id, event, icd_ms=0, max_triggers=0):
        old = self.procs.get(proc_id)
        if old is not None and old["event"] != event:
            old_subs = self._by_event.get(old["event"])
            if old_subs is not None:
                old_subs.discard(proc_id)
            self._sorted.pop(old["event"], None)
        self.procs[proc_id] = {"id": proc_id, "event": event, "icd_ms": icd_ms,
                               "max_triggers": max_triggers}
        self._by_event.setdefault(event, set()).add(proc_id)
        self._sorted.pop(event, None)
        self.state[proc_id] = {"last": None, "count": 0}

    def fire(self, event, now_ms, event_id, roll=0):
        """派发一次事件，返回被触发的 proc 列表。"""
        if event_id in self.handled:
            return []
        self.handled.add(event_id)
        out = []
        subscribers = self._sorted.get(event)
        if subscribers is None:
            subscribers = sorted(self._by_event.get(event, ()))
            self._sorted[event] = subscribers
        for proc_id in subscribers:
            self.scanned += 1
            proc = self.procs[proc_id]
            proc_state = self.state[proc_id]
            if proc["max_triggers"] > 0 and proc_state["count"] >= proc["max_triggers"]:
                continue
            last = proc_state["last"]
            if last is not None and now_ms - last < proc["icd_ms"]:
                continue
            proc_state["count"] += 1
            proc_state["last"] = now_ms
            out.append(proc_id)
        return out

    def triggers(self, proc_id):
        return self.state.get(proc_id, {}).get("count", 0)

    def scanned_count(self):
        return self.scanned
