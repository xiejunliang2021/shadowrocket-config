#!/usr/bin/env python3
"""Fetch only [Rule] from the official lazy_group.conf and render two profiles."""
from pathlib import Path
from urllib.request import Request, urlopen
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "config.template"
OUT = ROOT / "dist"
SOURCE_URL = (
    "https://raw.githubusercontent.com/Johnshall/"
    "Shadowrocket-ADBlock-Rules-Forever/release/lazy_group.conf"
)

def main():
    req = Request(SOURCE_URL, headers={"User-Agent": "shadowrocket-rule-sync/1.0"})
    with urlopen(req, timeout=40) as response:
        source = response.read().decode("utf-8-sig")

    match = re.search(
        r"(?ms)^\[Rule\]\s*\n(.*?)(?=^\[[^\r\n]+\]\s*$|\Z)",
        source,
    )
    if not match:
        raise RuntimeError("官方文件中没有找到 [Rule] 区域；停止生成，避免发布空规则。")

    rules = match.group(1).strip()
    if "FINAL,PROXY" not in rules or "RULE-SET," not in rules:
        raise RuntimeError("提取到的规则内容不完整；停止生成。")

    template = TEMPLATE.read_text(encoding="utf-8")
    if "{{RULES}}" not in template or "{{INTERVAL}}" not in template:
        raise RuntimeError("模板缺少 {{RULES}} 或 {{INTERVAL}} 占位符。")

    OUT.mkdir(parents=True, exist_ok=True)
    profiles = {
        "cellular.conf": "86400",
        "wifi.conf": "600",
    }

    # 所有检查通过后才写出文件；任何异常都不会覆盖现有 dist 文件。
    rendered = {}
    for filename, interval in profiles.items():
        text = template.replace("{{RULES}}", rules).replace("{{INTERVAL}}", interval)
        if "{{" in text or "}}" in text:
            raise RuntimeError(f"{filename} 仍存在未替换的模板变量。")
        if text.count("[Rule]") != 1 or text.count("[Proxy Group]") != 1:
            raise RuntimeError(f"{filename} 的配置段数量异常。")
        rendered[filename] = text.rstrip() + "\n"

    for filename, text in rendered.items():
        (OUT / filename).write_text(text, encoding="utf-8")

    print("已生成：dist/cellular.conf（86400 秒）和 dist/wifi.conf（600 秒）")
    print(f"规则来源：{SOURCE_URL}")
    print("同步范围仅为 [Rule]；[Proxy Group] 和其他本地模板内容保持不变。")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"构建失败：{exc}", file=sys.stderr)
        raise
