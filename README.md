# proc-engine

触发引擎：事件订阅索引、内部冷却、触发上限与事件幂等，只用 Python 标准库。

```
python3 -m procs.cli --sample event
python3 -m procs.cli --sample icd
python3 -m procs.cli --sample cap
python3 -m procs.cli --sample dup
python3 -m procs.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **事件索引**：只有订阅了本次 `event` 的 proc 参与判定，其他 proc 不受影响。
- **内部冷却（ICD）**：同一个 proc 距上次触发不足 `icd_ms` 时不再触发；
  正好等于 `icd_ms` 可以触发。
- **触发上限**：`max_triggers` 大于 0 时，proc 触发次数达到上限后不再触发。
- **事件幂等**：同一个 `event_id` 只处理一次，重复派发返回空列表。
- **不变量**：一次派发里同一个 proc 最多出现一次；`triggers` 只增不减；
  同一串派发序列重复执行结果相同。
- **查询代价**：派发不许扫描全部注册项，`scanned_count` 不随注册数线性增长。
- **规模**：10 万个 proc、每秒 10 万次派发，单次摊还 O(订阅该事件的 proc 数)。

## 输出契约（不改格式）

```
fired=..
second=..
triggers=..
scanned=..
```

## 目录

```
procs/core.py   订阅索引、ICD、上限与幂等
procs/cli.py    命令行入口
tests/          unittest 用例
```
