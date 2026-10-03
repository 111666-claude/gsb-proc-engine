"""命令行入口：跑触发引擎样例。"""

import argparse

from .core import Engine


def build_parser():
    parser = argparse.ArgumentParser(prog="proc-engine", description="触发引擎")
    parser.add_argument("--sample", default="event",
                        help="event / icd / cap / dup / scan")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "event":
        engine = Engine()
        engine.register("p1", "hit")
        engine.register("p2", "kill")
        print("fired=%s" % ",".join(engine.fire("hit", 0, "e1")))
    elif args.sample == "icd":
        engine = Engine()
        engine.register("p1", "hit", icd_ms=1000)
        engine.fire("hit", 0, "e1")
        print("second=%s" % ",".join(engine.fire("hit", 500, "e2")))
    elif args.sample == "cap":
        engine = Engine()
        engine.register("p1", "hit", max_triggers=2)
        for index in range(3):
            engine.fire("hit", index * 1000, "e-%d" % index)
        print("triggers=%d" % engine.triggers("p1"))
    elif args.sample == "dup":
        engine = Engine()
        engine.register("p1", "hit")
        engine.fire("hit", 0, "same")
        print("second=%s" % ",".join(engine.fire("hit", 0, "same")))
    elif args.sample == "scan":
        engine = Engine()
        for index in range(3000):
            engine.register("p-%d" % index, "hit")
        for index in range(3000):
            engine.fire("kill", index, "e-%d" % index)
        print("scanned=%d" % engine.scanned_count())
    else:
        raise SystemExit("需要 --sample event|icd|cap|dup|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
