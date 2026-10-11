#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiraSpeak — система контролю виконання плану (Plan-MiraSpeak-FULL.md).

Команди:
  python tools/progress.py status                # зведена статистика (типова)
  python tools/progress.py list [--block N] [--kind auto|manual]
  python tools/progress.py run [ID ...] [--block N] [--all] [--force]
  python tools/progress.py pass ID ... [-r "вердикт"]    # фізичний тест: успіх
  python tools/progress.py fail ID ... [-r "вердикт"]    # фізичний тест: невдача
  python tools/progress.py undo ID ...           # скинути позначку в ⏳
  python tools/progress.py report                # перегенерувати EXECUTION-STATUS.md

Статуси: ⏳ pending | ✅ pass | ❌ fail | ⛔ blocked (немає передумов) | (опц.) не впливає на %
Типи: auto — синтетичний тест (виконує трекер); manual — фізичний тест (вердикт користувача).
Стан: tools/execution-state.json · Звіт: EXECUTION-STATUS.md
"""
import argparse
import datetime
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))
from checkpoints import BLOCKS, CHECKPOINTS  # noqa: E402

STATE_FILE = TOOLS_DIR / "execution-state.json"
REPORT_FILE = ROOT / "EXECUTION-STATUS.md"
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"

SYMBOLS = {"pending": "⏳", "pass": "✅", "fail": "❌", "blocked": "⛔"}
BY_ID = {cp["id"]: cp for cp in CHECKPOINTS}


def now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"updated": None, "results": {}}


def save_state(state: dict) -> None:
    state["updated"] = now()
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def status_of(state: dict, cp: dict) -> str:
    rec = state["results"].get(cp["id"])
    return rec["status"] if rec else "pending"


def is_active(cp: dict) -> bool:
    return not cp.get("optional")


def http_ok(url: str, timeout: float = 3.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def requirement(req: str) -> tuple[bool, str]:
    """Повертає (умова виконана, пояснення для blocked)."""
    if req == "venv":
        return VENV_PY.exists(), "venv не створено — виконай Блок 2, крок 3"
    if req == "server":
        return http_ok("http://127.0.0.1:8000/api/health"), \
            "сервер не запущений — python -m app.main"
    if req == "ollama":
        return http_ok("http://127.0.0.1:11434/api/tags"), \
            "Ollama API недоступний — запусти Ollama"
    return True, ""


def run_check(cp: dict) -> dict:
    """Виконує синтетичний тест; повертає запис результату."""
    # передумови
    needed = list(cp.get("requires") or [])
    if "{py}" in cp["check"] and "venv" not in needed:
        needed.append("venv")
    for req in needed:
        ok, why = requirement(req)
        if not ok:
            return {"status": "blocked", "result": why, "output": "", "duration": None}

    cmd = cp["check"].replace("{py}", f'"{VENV_PY}"')
    timeout = cp.get("timeout", 60)
    import time
    t0 = time.monotonic()
    try:
        if cmd.startswith("git "):
            # без shell: cmd.exe з'їв би % у --pretty=%s
            proc = subprocess.run(cmd.split(), cwd=ROOT, capture_output=True,
                                  text=True, encoding="utf-8", errors="replace",
                                  timeout=timeout)
        else:
            proc = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True,
                                  text=True, encoding="utf-8", errors="replace",
                                  timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"status": "fail", "result": f"перевищено тайм-аут {timeout} с",
                "output": "", "duration": round(time.monotonic() - t0, 2)}
    except Exception as e:
        return {"status": "fail", "result": f"помилка запуску: {e}",
                "output": "", "duration": round(time.monotonic() - t0, 2)}

    dur = round(time.monotonic() - t0, 2)
    combined = (proc.stdout or "") + (proc.stderr or "")
    expect = cp.get("expect")
    if proc.returncode != 0:
        result = f"код виходу {proc.returncode}"
        status = "fail"
    elif expect and expect.lower() not in combined.lower():
        result = f"не знайдено «{expect}»"
        status = "fail"
    else:
        result = f"OK ({dur} с)"
        status = "pass"
    output = combined.strip()[-800:]
    return {"status": status, "result": result, "output": output, "duration": dur}


def counts(state: dict) -> dict:
    """Агреговані лічильники по активних (неопційних) контрольних точках."""
    res = {"total": 0, "pass": 0, "fail": 0, "blocked": 0, "pending": 0,
           "auto_total": 0, "auto_pass": 0, "manual_total": 0, "manual_pass": 0,
           "optional": 0}
    for cp in CHECKPOINTS:
        if not is_active(cp):
            res["optional"] += 1
            continue
        st = status_of(state, cp)
        res["total"] += 1
        res[st] = res.get(st, 0) + 1
        kind = "auto" if cp["kind"] == "auto" else "manual"
        res[f"{kind}_total"] += 1
        if st == "pass":
            res[f"{kind}_pass"] += 1
    return res


def bar(done: int, total: int, width: int = 20) -> str:
    if total <= 0:
        return ""
    filled = round(width * done / total)
    return "█" * filled + "░" * (width - filled)


def print_status(state: dict) -> None:
    c = counts(state)
    pct = round(100 * c["pass"] / c["total"]) if c["total"] else 0
    print("═" * 72)
    print(" MiraSpeak — контроль виконання плану")
    print("═" * 72)
    print(f" Загальний прогрес : {bar(c['pass'], c['total'])} {c['pass']}/{c['total']} ({pct}%)")
    print(f" Синтетичні (auto) : {c['auto_pass']}/{c['auto_total']}   "
          f"Фізичні (manual): {c['manual_pass']}/{c['manual_total']}")
    print(f" Статуси           : ✅ {c['pass']}   ❌ {c['fail']}   "
          f"⛔ {c['blocked']}   ⏳ {c['pending']}"
          + (f"   (+{c['optional']} опційних)" if c["optional"] else ""))
    print("─" * 72)
    for block in sorted(BLOCKS):
        cps = [cp for cp in CHECKPOINTS if cp["block"] == block]
        done = sum(1 for cp in cps if is_active(cp) and status_of(state, cp) == "pass")
        total = sum(1 for cp in cps if is_active(cp))
        print(f" Блок {block}: {bar(done, total, 14)} {done}/{total}  {BLOCKS[block]}")
    fails = [cp for cp in CHECKPOINTS if status_of(state, cp) == "fail"]
    blocked = [cp for cp in CHECKPOINTS if status_of(state, cp) == "blocked"]
    if fails:
        print("─" * 72)
        print(" ❌ Невдалі:")
        for cp in fails:
            rec = state["results"].get(cp["id"], {})
            print(f"    {cp['id']} — {cp['title']}  [{rec.get('result', '')}]")
    if blocked:
        print("─" * 72)
        print(" ⛔ Заблоковані (немає передумов):")
        for cp in blocked:
            rec = state["results"].get(cp["id"], {})
            print(f"    {cp['id']} — {cp['title']}  [{rec.get('result', '')}]")
    pending = [cp for cp in CHECKPOINTS if status_of(state, cp) == "pending"]
    if pending:
        print("─" * 72)
        print(" ⏳ Найближчі невиконані:")
        for cp in pending[:6]:
            kind = "синт" if cp["kind"] == "auto" else "ФІЗ"
            print(f"    {cp['id']} [{kind}] — {cp['title']}")
    print("═" * 72)


def cmd_list(state: dict, block: int | None, kind: str | None) -> None:
    for cp in CHECKPOINTS:
        if block and cp["block"] != block:
            continue
        if kind and cp["kind"] != kind:
            continue
        st = status_of(state, cp)
        rec = state["results"].get(cp["id"], {})
        opt = " (опц.)" if cp.get("optional") else ""
        kind_lbl = "синт" if cp["kind"] == "auto" else "ФІЗ"
        extra = f"  → {rec.get('result')}" if rec.get("result") else ""
        print(f"{SYMBOLS[st]} {cp['id']:<9} [{kind_lbl}] {cp['title']}{opt}{extra}")

def cmd_run(state: dict, ids: list[str], block: int | None,
            run_all: bool, force: bool) -> int:
    if ids:
        targets = []
        for raw in ids:
            cid = raw.upper()
            if cid not in BY_ID:
                print(f"⚠ Невідомий ID: {raw}")
                return 2
            targets.append(BY_ID[cid])
    elif run_all or block:
        targets = CHECKPOINTS
    else:
        print("Вкажи ID, --block N або --all. Приклад: run B2-1 B2-2")
        return 2

    failures = 0
    for cp in targets:
        if block and cp["block"] != block:
            continue
        if cp["kind"] != "auto":
            print(f"→ {cp['id']} — фізичний тест; використовуй: pass/fail {cp['id']} -r \"вердикт\"")
            continue
        prev = status_of(state, cp)
        if prev == "pass" and not force:
            print(f"→ {cp['id']} — вже ✅ (перезапуск: --force)")
            continue
        print(f"→ {cp['id']} — {cp['title']} ...", end=" ", flush=True)
        rec = run_check(cp)
        rec["at"] = now()
        rec["kind"] = "auto"
        state["results"][cp["id"]] = rec
        print(f"{SYMBOLS[rec['status']]} {rec['result']}")
        if rec["status"] == "fail":
            failures += 1
            if rec.get("output"):
                print("   └ вивід:", rec["output"][:300].replace("\n", " ⏎ "))
    return 1 if failures else 0


def cmd_verdict(state: dict, status: str, ids: list[str], result: str) -> int:
    rc = 0
    for raw in ids:
        cid = raw.upper()
        if cid not in BY_ID:
            print(f"⚠ Невідомий ID: {raw}")
            rc = 2
            continue
        cp = BY_ID[cid]
        if not result:
            kind_hint = ("вкажи причину: -r \"що саме сталося\""
                         if cp["kind"] == "auto"
                         else f"потрібен вердикт: -r \"оцінка/спостереження\"")
            print(f"⚠ {cid}: {kind_hint}")
            rc = 2
            continue
        state["results"][cid] = {
            "status": status,
            "result": result,
            "output": "",
            "duration": None,
            "at": now(),
            "kind": cp["kind"],
            "by": "user",
        }
        print(f"{SYMBOLS[status]} {cid} — {cp['title']}")
        print(f"   └ {result}")
    return rc


def cmd_undo(state: dict, ids: list[str]) -> int:
    rc = 0
    for raw in ids:
        cid = raw.upper()
        if cid not in BY_ID:
            print(f"⚠ Невідомий ID: {raw}")
            rc = 2
            continue
        state["results"].pop(cid, None)
        print(f"⏳ {cid} — скинуто в pending")
    return rc

def _md(text: str) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ⏎ ")


def write_report(state: dict) -> None:
    c = counts(state)
    pct = round(100 * c["pass"] / c["total"]) if c["total"] else 0
    L: list[str] = []
    L.append("# MiraSpeak — статус виконання плану\n")
    L.append("> Автоматично згенеровано `python tools/progress.py report`. "
             f"Оновлено: {now()}\n")
    L.append("## Підсумок\n")
    L.append("| Метрика | Значення |")
    L.append("|---|---|")
    L.append(f"| **Загальний прогрес** | **{c['pass']}/{c['total']} ({pct}%)** "
             f"{bar(c['pass'], c['total'], 14)} |")
    L.append(f"| Синтетичні тести (auto) | {c['auto_pass']}/{c['auto_total']} |")
    L.append(f"| Фізичні тести користувача (manual) | {c['manual_pass']}/{c['manual_total']} |")
    L.append(f"| Статуси | ✅ {c['pass']} · ❌ {c['fail']} · "
             f"⛔ {c['blocked']} · ⏳ {c['pending']} |")
    if c["optional"]:
        L.append(f"| Опційні (не впливають на %) | {c['optional']} |")
    L.append("")

    fails = [cp for cp in CHECKPOINTS if status_of(state, cp) == "fail"]
    blocked = [cp for cp in CHECKPOINTS if status_of(state, cp) == "blocked"]
    pending = [cp for cp in CHECKPOINTS if status_of(state, cp) == "pending"]
    if fails:
        L.append("## ❌ Невдалі перевірки\n")
        L.append("| ID | Крок | Результат | Коли |")
        L.append("|---|---|---|---|")
        for cp in fails:
            r = state["results"].get(cp["id"], {})
            L.append(f"| {cp['id']} | {_md(cp['title'])} | "
                     f"{_md(r.get('result', ''))} | {r.get('at', '')} |")
        L.append("")
    if blocked:
        L.append("## ⛔ Заблоковані (немає передумов)\n")
        L.append("| ID | Крок | Причина |")
        L.append("|---|---|---|")
        for cp in blocked:
            r = state["results"].get(cp["id"], {})
            L.append(f"| {cp['id']} | {_md(cp['title'])} | {_md(r.get('result', ''))} |")
        L.append("")
    if pending:
        L.append("## ⏳ Далі виконувати\n")
        for i, cp in enumerate(pending[:10], 1):
            kind = "синт" if cp["kind"] == "auto" else "**ФІЗ**"
            opt = " *(опц.)*" if cp.get("optional") else ""
            L.append(f"{i}. `{cp['id']}` [{kind}] {cp['title']}{opt}")
        L.append("")

    L.append("## Деталізація по блоках\n")
    for block in sorted(BLOCKS):
        cps = [cp for cp in CHECKPOINTS if cp["block"] == block]
        done = sum(1 for cp in cps if is_active(cp) and status_of(state, cp) == "pass")
        total = sum(1 for cp in cps if is_active(cp))
        L.append(f"### Блок {block} — {BLOCKS[block]}  ({done}/{total})\n")
        L.append("| ID | Тип | Крок | Статус | Результат / вердикт | Коли |")
        L.append("|---|---|---|---|---|---|")
        for cp in cps:
            st = status_of(state, cp)
            r = state["results"].get(cp["id"], {})
            typ = "синт" if cp["kind"] == "auto" else "ФІЗ"
            opt = " *(опц.)*" if cp.get("optional") else ""
            L.append(f"| `{cp['id']}` | {typ} | {_md(cp['title'])}{opt} | "
                     f"{SYMBOLS[st]} {st} | {_md(r.get('result', ''))} | "
                     f"{r.get('at', '')} |")
        L.append("")

    detailed = [cp for cp in CHECKPOINTS
                if state["results"].get(cp["id"], {}).get("output")]
    if detailed:
        L.append("## Виводи синтетичних тестів\n")
        for cp in detailed:
            r = state["results"][cp["id"]]
            L.append(f"<details><summary><code>{cp['id']}</code> — {cp['title']} "
                     f"({SYMBOLS[r['status']]})</summary>\n")
            L.append("```")
            L.append(r["output"])
            L.append("```\n</details>\n")
    REPORT_FILE.write_text("\n".join(L), encoding="utf-8")

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="progress",
        description="Контроль виконання плану MiraSpeak: синтетичні та фізичні тести.",
        epilog="Приклади:\n"
               "  python tools/progress.py run B2-1 B2-2\n"
               "  python tools/progress.py run --block 3\n"
               "  python tools/progress.py pass B6-M1 -r \"UI ок, оцінка 9/10\"\n"
               "  python tools/progress.py fail B3-M1 -r \"UK-голос металевий, 4/10\"\n",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("status", help="зведена статистика")
    lp = sub.add_parser("list", help="список контрольних точок")
    lp.add_argument("--block", type=int, choices=sorted(BLOCKS))
    lp.add_argument("--kind", choices=["auto", "manual"])
    rp = sub.add_parser("run", help="виконати синтетичні тести")
    rp.add_argument("ids", nargs="*")
    rp.add_argument("--block", type=int, choices=sorted(BLOCKS))
    rp.add_argument("--all", action="store_true")
    rp.add_argument("--force", action="store_true", help="перезапустити навіть ✅")
    for name, h in (("pass", "успіх"), ("fail", "невдача")):
        sp = sub.add_parser(name, help=f"вердикт ({h})")
        sp.add_argument("ids", nargs="+")
        sp.add_argument("-r", "--result", default="", help="результат / оцінка")
    up = sub.add_parser("undo", help="скинути позначку в pending")
    up.add_argument("ids", nargs="+")
    sub.add_parser("report", help="перегенерувати EXECUTION-STATUS.md")

    args = p.parse_args(argv)
    state = load_state()
    cmd = args.cmd or "status"
    rc = 0
    if cmd == "status":
        print_status(state)
    elif cmd == "list":
        cmd_list(state, args.block, args.kind)
    elif cmd == "run":
        rc = cmd_run(state, args.ids, args.block, args.all, args.force)
    elif cmd in ("pass", "fail"):
        rc = cmd_verdict(state, cmd, args.ids, args.result)
    elif cmd == "undo":
        rc = cmd_undo(state, args.ids)

    if cmd in ("run", "pass", "fail", "undo", "report"):
        save_state(state)
        write_report(state)
        print(f"📄 Звіт оновлено: {REPORT_FILE}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())



