#!/usr/bin/env python3
"""
字幕烧录脚本：使用 ffmpeg 将 SRT 字幕烧录到视频中。

用法:
    python3 burn_subtitle.py --input edited.mp4 --subtitle subtitle.srt --output final.mp4 [选项]

依赖:
    ffmpeg (命令行工具)
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_ffmpeg() -> bool:
    """检查 ffmpeg 是否已安装。"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def burn_subtitle(
    input_path: str,
    subtitle_path: str,
    output_path: str,
    font: str = "Noto Sans CJK SC",
    fontsize: int = 24,
    fontcolor: str = "white",
    outline: int = 2,
    margin_v: int = 40,
) -> bool:
    """使用 ffmpeg subtitles 滤镜将字幕烧录到视频。"""

    # 构建 subtitles 滤镜参数
    # 注意：ffmpeg subtitles 滤镜中路径需要转义冒号和反斜杠
    escaped_sub_path = subtitle_path.replace("\\", "\\\\").replace(":", "\\:")
    subtitle_filter = (
        f"subtitles='{escaped_sub_path}':"
        f"force_style='FontName={font},"
        f"FontSize={fontsize},"
        f"PrimaryColour=&H00FFFFFF,"  # 白色
        f"OutlineColour=&H00000000,"  # 黑色描边
        f"Outline={outline},"
        f"MarginV={margin_v},"
        f"Alignment=2'"  # 底部居中
    )

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", subtitle_filter,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "copy",
        "-y",
        output_path,
    ]

    print(f"正在烧录字幕...")
    print(f"  字体: {font}")
    print(f"  字号: {fontsize}")
    print(f"  描边: {outline}px")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: 字幕烧录失败")
        # 输出错误的最后几行
        stderr_lines = e.stderr.strip().split("\n")
        for line in stderr_lines[-5:]:
            print(f"  {line}")
        return False


def main():
    parser = argparse.ArgumentParser(description="将 SRT 字幕烧录到视频中")
    parser.add_argument("--input", "-i", required=True, help="输入视频文件路径")
    parser.add_argument("--subtitle", "-s", required=True, help="SRT 字幕文件路径")
    parser.add_argument("--output", "-o", required=True, help="输出视频文件路径")
    parser.add_argument("--font", default="Noto Sans CJK SC", help="字体名称 (默认: Noto Sans CJK SC)")
    parser.add_argument("--fontsize", type=int, default=24, help="字号 (默认: 24)")
    parser.add_argument("--outline", type=int, default=2, help="描边粗细 (默认: 2)")
    parser.add_argument("--margin-v", type=int, default=40, help="底部边距 (默认: 40)")
    args = parser.parse_args()

    if not check_ffmpeg():
        print("错误: 未找到 ffmpeg，请先安装: brew install ffmpeg")
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 输入视频不存在: {input_path}")
        sys.exit(1)

    subtitle_path = Path(args.subtitle)
    if not subtitle_path.exists():
        print(f"错误: 字幕文件不存在: {subtitle_path}")
        sys.exit(1)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if burn_subtitle(
        str(input_path),
        str(subtitle_path),
        str(output),
        font=args.font,
        fontsize=args.fontsize,
        outline=args.outline,
        margin_v=args.margin_v,
    ):
        print(f"\n✅ 带字幕视频已生成: {output}")
    else:
        print("\n❌ 字幕烧录失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
