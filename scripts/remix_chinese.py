#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def call_deepseek(api_key, model, source_text):
    system_prompt = (
        "你是 AI Builder 每日中文摘要编辑。请把输入的 AI 速报改写成精炼、自然的中文简报。"
        "要求：不要编造事实；保留每条内容的来源链接；人名、产品名和英文品牌保留英文原名；"
        "输出 Markdown；整体控制在 600-900 字左右。"
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": source_text},
        ],
        "temperature": 0.4,
        "max_tokens": 2000,
    }
    request = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))
    try:
        return result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        raise SystemExit(f"DeepSeek 返回格式异常：{result}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print("skip: no input digest file")
        return

    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print("skip: DEEPSEEK_API_KEY is not configured, keeping structured digest")
        return

    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash").strip()
    source_text = input_path.read_text(encoding="utf-8")

    try:
        digest = call_deepseek(api_key, model, source_text)
    except Exception as exc:
        print(f"DeepSeek call failed, keeping structured digest: {exc}")
        return

    Path(args.output).write_text(digest + "\n", encoding="utf-8")
    print("DeepSeek Chinese digest generated")


if __name__ == "__main__":
    main()
