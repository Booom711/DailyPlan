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
        if result.get("code") == 905:
            raise SystemExit(
                "PushPlus 账户未实名认证，请先访问 https://verify.pushplus.plus 完成认证后再推送。"
            )
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


def send_wxpusher(spt, title, markdown):
    payload = {
        "content": markdown,
        "summary": title,
        "contentType": 3,
        "spt": spt,
    }
    request = urllib.request.Request(
        "https://wxpusher.zjiecode.com/api/send/message/simple-push",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("code") != 1000:
        raise SystemExit(f"WxPusher 推送失败：{result}")


def main():
    dry_run = "--dry-run" in sys.argv
    digest_file = None
    target_date = datetime.now(CHINA_TZ)
    args = sys.argv[1:]
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--digest-file":
            index += 1
            digest_file = args[index]
        elif arg.startswith("--digest-file="):
            digest_file = arg.split("=", 1)[1]
        elif arg == "--dry-run":
            pass
        else:
            index += 1
            continue
        index += 1

    for arg in args:
        if arg.startswith("--date="):
            target_date = datetime.strptime(arg.split("=", 1)[1], "%Y-%m-%d").replace(
                tzinfo=CHINA_TZ
            )

    data = load_plan()
    day = data["days"][target_date.weekday()]
    title, markdown = render_plan(data, day, target_date)

    if digest_file:
        digest_path = Path(digest_file)
        if digest_path.exists():
            digest_md = digest_path.read_text(encoding="utf-8").strip()
            if digest_md:
                title = f"{target_date.year}-{target_date.month:02d}-{target_date.day:02d} {day['weekday']} | 健身计划 + AI 速报"
                markdown = digest_md + "\n\n---\n\n" + markdown

    if dry_run:
        print(title)
        print(markdown)
        return

    provider = os.environ.get("PUSH_PROVIDER", "auto").strip().lower()
    if provider == "auto":
        if os.environ.get("SERVERCHAN_SENDKEY", "").strip():
            provider = "serverchan"
        elif os.environ.get("WXPUSHER_SPT", "").strip():
            provider = "wxpusher"
        elif os.environ.get("PUSHPLUS_TOKEN", "").strip():
            provider = "pushplus"
        else:
            raise SystemExit(
                "未检测到推送 token，请配置 SERVERCHAN_SENDKEY、WXPUSHER_SPT 或 PUSHPLUS_TOKEN。"
            )

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
    elif provider == "wxpusher":
        spt = os.environ.get("WXPUSHER_SPT", "").strip()
        if not spt:
            raise SystemExit("缺少 WXPUSHER_SPT，请在 GitHub Actions secrets 中配置。")
        send_wxpusher(spt, title, markdown)
    else:
        raise SystemExit(f"不支持的 PUSH_PROVIDER：{provider}")

    print(f"已推送：{title}")


if __name__ == "__main__":
    main()
