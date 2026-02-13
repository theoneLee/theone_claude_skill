#!/usr/bin/env python3
"""
SRT 字幕生成脚本：将 Whisper 转录 JSON 转换为 SRT 字幕文件。

用法:
    python3 generate_srt.py --input transcript.json --output subtitle.srt [--max-chars 20]
"""

import argparse
import json
import sys
from pathlib import Path


def format_timestamp(seconds: float) -> str:
    """将秒数转换为 SRT 时间戳格式: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def split_text(text: str, max_chars: int) -> list[str]:
    """将长文本按标点或字数拆分为多行。"""
    if len(text) <= max_chars:
        return [text]

    lines = []
    # 优先在标点处分割
    split_points = ["，", "。", "！", "？", "；", "、", ",", ".", "!", "?", " "]

    remaining = text
    while len(remaining) > max_chars:
        # 在 max_chars 范围内找最后一个分割点
        best_pos = -1
        for punct in split_points:
            pos = remaining[:max_chars].rfind(punct)
            if pos > best_pos:
                best_pos = pos

        if best_pos > 0:
            lines.append(remaining[: best_pos + 1].strip())
            remaining = remaining[best_pos + 1 :].strip()
        else:
            # 没有合适的分割点，强制按字数分割
            lines.append(remaining[:max_chars])
            remaining = remaining[max_chars:]

    if remaining.strip():
        lines.append(remaining.strip())

    return lines


def generate_srt(segments: list[dict], max_chars: int = 20) -> str:
    """从转录段落生成 SRT 字幕内容。"""
    srt_entries = []
    index = 1

    for seg in segments:
        text = seg.get("text", "").strip()
        if not text:
            continue

        start = seg.get("start", 0)
        end = seg.get("end", 0)
        duration = end - start

        # 将长段落拆分
        lines = split_text(text, max_chars)

        if len(lines) == 1:
            entry = f"{index}\n{format_timestamp(start)} --> {format_timestamp(end)}\n{lines[0]}\n"
            srt_entries.append(entry)
            index += 1
        else:
            # 按行数均分时间
            time_per_line = duration / len(lines)
            for i, line in enumerate(lines):
                line_start = start + i * time_per_line
                line_end = start + (i + 1) * time_per_line
                entry = f"{index}\n{format_timestamp(line_start)} --> {format_timestamp(line_end)}\n{line}\n"
                srt_entries.append(entry)
                index += 1

    return "\n".join(srt_entries)


def main():
    parser = argparse.ArgumentParser(description="Whisper 转录 JSON → SRT 字幕文件")
    parser.add_argument("--input", "-i", required=True, help="输入转录 JSON 文件路径")
    parser.add_argument("--output", "-o", required=True, help="输出 SRT 文件路径")
    parser.add_argument("--max-chars", type=int, default=20, help="每行最大字数 (默认: 20)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        transcript = json.load(f)

    segments = transcript.get("segments", [])
    if not segments:
        print("错误: 转录结果中没有段落")
        sys.exit(1)

    srt_content = generate_srt(segments, args.max_chars)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    # 统计
    entry_count = srt_content.count("\n\n") + 1
    print(f"✅ SRT 字幕已生成: {output_path}")
    print(f"   字幕条数: {entry_count}")
    print(f"   每行最大字数: {args.max_chars}")


if __name__ == "__main__":
    main()
