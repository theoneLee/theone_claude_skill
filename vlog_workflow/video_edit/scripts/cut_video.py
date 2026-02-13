#!/usr/bin/env python3
"""
视频剪辑脚本：根据剪辑方案（保留区间 JSON）使用 ffmpeg 执行精确剪辑。

用法:
    python3 cut_video.py --input raw.mp4 --plan cut_plan.json --output edited.mp4

依赖:
    ffmpeg (命令行工具)

cut_plan.json 格式:
{
    "keep_segments": [
        {"start": 0.0, "end": 45.2, "note": "开场白"},
        {"start": 48.5, "end": 120.3, "note": "第一部分"}
    ]
}
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def check_ffmpeg() -> bool:
    """检查 ffmpeg 是否已安装。"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_video_duration(video_path: str) -> float:
    """获取视频时长。"""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        video_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    except (subprocess.CalledProcessError, KeyError, ValueError):
        return 0.0


def cut_segment(input_path: str, output_path: str, start: float, end: float) -> bool:
    """使用 ffmpeg 剪切单个片段。"""
    duration = end - start
    cmd = [
        "ffmpeg",
        "-ss", f"{start:.3f}",
        "-i", input_path,
        "-t", f"{duration:.3f}",
        "-c", "copy",            # 不重新编码，速度快
        "-avoid_negative_ts", "make_zero",
        "-y",
        output_path,
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  警告: 快速剪切失败，尝试重新编码...")
        # 回退到重新编码模式
        cmd_reencode = [
            "ffmpeg",
            "-ss", f"{start:.3f}",
            "-i", input_path,
            "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            "-y",
            output_path,
        ]
        try:
            subprocess.run(cmd_reencode, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e2:
            print(f"  错误: 片段剪切失败: {e2.stderr[:200]}")
            return False


def concat_segments(segment_files: list[str], output_path: str) -> bool:
    """使用 ffmpeg concat 拼接所有片段。"""
    # 创建 concat 列表文件
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for seg_file in segment_files:
            f.write(f"file '{seg_file}'\n")
        concat_list = f.name

    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        "-y",
        output_path,
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        # 回退到重新编码
        cmd_reencode = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            "-y",
            output_path,
        ]
        try:
            subprocess.run(cmd_reencode, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"错误: 拼接失败: {e.stderr[:200]}")
            return False
    finally:
        Path(concat_list).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="根据剪辑方案执行视频剪辑")
    parser.add_argument("--input", "-i", required=True, help="输入视频文件路径")
    parser.add_argument("--plan", "-p", required=True, help="剪辑方案 JSON 文件路径")
    parser.add_argument("--output", "-o", required=True, help="输出视频文件路径")
    args = parser.parse_args()

    if not check_ffmpeg():
        print("错误: 未找到 ffmpeg，请先安装: brew install ffmpeg")
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 输入视频不存在: {input_path}")
        sys.exit(1)

    # 读取剪辑方案
    with open(args.plan, "r", encoding="utf-8") as f:
        plan = json.load(f)

    segments = plan.get("keep_segments", [])
    if not segments:
        print("错误: 剪辑方案中没有保留片段")
        sys.exit(1)

    # 按 start 排序
    segments.sort(key=lambda s: s["start"])

    original_duration = get_video_duration(str(input_path))
    total_kept = sum(s["end"] - s["start"] for s in segments)

    print(f"原始视频时长: {original_duration:.1f} 秒")
    print(f"保留片段数: {len(segments)}")
    print(f"保留时长: {total_kept:.1f} 秒")
    print(f"剪除时长: {original_duration - total_kept:.1f} 秒")
    print()

    # 逐段剪切
    tmp_dir = tempfile.mkdtemp()
    segment_files = []

    for i, seg in enumerate(segments):
        seg_file = f"{tmp_dir}/seg_{i:04d}.mp4"
        note = seg.get("note", "")
        print(f"  剪切片段 {i+1}/{len(segments)}: [{seg['start']:.1f}s - {seg['end']:.1f}s] {note}")

        if not cut_segment(str(input_path), seg_file, seg["start"], seg["end"]):
            print(f"  错误: 片段 {i+1} 剪切失败，跳过")
            continue

        segment_files.append(seg_file)

    if not segment_files:
        print("错误: 没有成功剪切的片段")
        sys.exit(1)

    # 拼接
    print(f"\n拼接 {len(segment_files)} 个片段...")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if concat_segments(segment_files, str(output_path)):
        final_duration = get_video_duration(str(output_path))
        print(f"\n✅ 剪辑完成: {output_path}")
        print(f"   最终时长: {final_duration:.1f} 秒")
        print(f"   减少: {original_duration - final_duration:.1f} 秒 ({(1 - final_duration/original_duration)*100:.1f}%)")
    else:
        print("错误: 视频拼接失败")
        sys.exit(1)

    # 清理临时文件
    for f in segment_files:
        Path(f).unlink(missing_ok=True)
    Path(tmp_dir).rmdir()


if __name__ == "__main__":
    main()
