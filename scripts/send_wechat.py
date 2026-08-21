#!/usr/bin/env python3
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CHINA_TZ = timezone(timedelta(hours=8))


def load_plan():
    path = ROOT / "plans" / "weekly.json"
    return json.loads(path.read_text(encoding="utf-8"))


def render_plan(data, day, target_date):
    title = f"{target_date.year}-{target_date.month:02d}-{target_date.day:02d} {day['weekday']} | {data['title']}"
    lines = [
        f"## 今日训练",
        day["training"],
        "",
        "## 今日饮食",
    ]
    for meal, content in day["diet"].items():
        lines.append(f"- **{meal}**：{content}")
    lines.extend(["", f"> {data['note']}"])
    return title, "\n".join(lines)


def send_pushplus(token, title, markdown):
    payload = {
        "token": token,
        "title": title,
        "content": markdown,
        "template": "markdown",
        "channel": "wechat",
    }
    request = urllib.request.Request(
        "https://www.pushplus.plus/send",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("code") != 200:
        raise SystemExit(f"PushPlus 推送失败：{result}")


def send_serverchan(sendkey, title, markdown):
    payload = urllib.parse.urlencode(
        {"title": title, "desp": markdown}
    ).encode("utf-8")
    request = urllib.request.Request(
        f"https://sctapi.ftqq.com/{sendkey}.send",
        data=payload,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("code") != 0:
        raise SystemExit(f"Server酱推送失败：{result}")


def main():
    dry_run = "--dry-run" in sys.argv
    target_date = datetime.now(CHINA_TZ)
    for arg in sys.argv[1:]:
        if arg.startswith("--date="):
            target_date = datetime.strptime(arg.split("=", 1)[1], "%Y-%m-%d").replace(
                tzinfo=CHINA_TZ
            )

    data = load_plan()
    day = data["days"][target_date.weekday()]
    title, markdown = render_plan(data, day, target_date)

    if dry_run:
        print(title)
        print(markdown)
        return

    provider = os.environ.get("PUSH_PROVIDER", "pushplus").strip().lower()
    if provider == "pushplus":
        token = os.environ.get("PUSHPLUS_TOKEN", "").strip()
        if not token:
            raise SystemExit("缺少 PUSHPLUS_TOKEN，请在 GitHub Actions secrets 中配置。")
        send_pushplus(token, title, markdown)
    elif provider == "serverchan":
        sendkey = os.environ.get("SERVERCHAN_SENDKEY", "").strip()
        if not sendkey:
            raise SystemExit("缺少 SERVERCHAN_SENDKEY，请在 GitHub Actions secrets 中配置。")
        send_serverchan(sendkey, title, markdown)
    else:
        raise SystemExit(f"不支持的 PUSH_PROVIDER：{provider}")

    print(f"已推送：{title}")


if __name__ == "__main__":
    main()
