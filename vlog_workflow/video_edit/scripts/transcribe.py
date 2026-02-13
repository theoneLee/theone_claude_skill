#!/usr/bin/env python3
"""
语音识别脚本：调用 speaches (faster-whisper) API 对视频/音频进行转录。

用法:
    python3 transcribe.py --input video.mp4 --output transcript.json [--api-url http://localhost:8000]

依赖:
    pip install requests

前置条件:
    speaches Docker 服务已启动: docker compose up -d
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import requests
except ImportError:
    print("错误: 请先安装 requests: pip install requests")
    sys.exit(1)


def extract_audio(video_path: str, audio_path: str) -> bool:
    """使用 ffmpeg 从视频中提取音频。"""
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn",                    # 不要视频
        "-acodec", "pcm_s16le",   # WAV 格式
        "-ar", "16000",           # 16kHz 采样率（Whisper 推荐）
        "-ac", "1",               # 单声道
        "-y",                     # 覆盖已有文件
        audio_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: ffmpeg 提取音频失败: {e.stderr}")
        return False
    except FileNotFoundError:
        print("错误: 未找到 ffmpeg，请先安装: brew install ffmpeg")
        return False


def transcribe_audio(audio_path: str, api_url: str) -> dict:
    """调用 speaches OpenAI 兼容 API 进行语音识别。"""
    url = f"{api_url}/v1/audio/transcriptions"

    with open(audio_path, "rb") as f:
        files = {"file": (Path(audio_path).name, f, "audio/wav")}
        data = {
            "model": "large-v3",
            "language": "zh",
            "response_format": "verbose_json",
            "timestamp_granularities[]": "segment",
        }
        print(f"正在调用语音识别 API: {url}")
        print("这可能需要几分钟，取决于视频长度...")

        try:
            response = requests.post(url, files=files, data=data, timeout=3600)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            print(f"错误: 无法连接到 speaches 服务 ({api_url})")
            print("请确保 Docker 服务已启动: docker compose up -d")
            sys.exit(1)
        except requests.HTTPError as e:
            print(f"错误: API 返回错误: {e.response.status_code} - {e.response.text}")
            sys.exit(1)


def format_transcript(raw_result: dict) -> dict:
    """格式化转录结果为统一的 JSON 结构。"""
    segments = []
    for seg in raw_result.get("segments", []):
        segments.append({
            "start": round(seg.get("start", 0), 2),
            "end": round(seg.get("end", 0), 2),
            "text": seg.get("text", "").strip(),
        })

    return {
        "language": raw_result.get("language", "zh"),
        "duration": raw_result.get("duration", 0),
        "text": raw_result.get("text", ""),
        "segments": segments,
    }


def main():
    parser = argparse.ArgumentParser(description="视频/音频语音识别（调用 speaches API）")
    parser.add_argument("--input", "-i", required=True, help="输入视频/音频文件路径")
    parser.add_argument("--output", "-o", required=True, help="输出 JSON 文件路径")
    parser.add_argument("--api-url", default="http://localhost:8000", help="speaches API 地址 (默认: http://localhost:8000)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}")
        sys.exit(1)

    # 判断是否需要提取音频
    audio_exts = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}
    if input_path.suffix.lower() in audio_exts:
        audio_path = str(input_path)
    else:
        # 视频文件，先提取音频
        print(f"从视频中提取音频: {input_path}")
        tmp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_audio.close()
        audio_path = tmp_audio.name

        if not extract_audio(str(input_path), audio_path):
            sys.exit(1)

    # 进行转录
    raw_result = transcribe_audio(audio_path, args.api_url)
    transcript = format_transcript(raw_result)

    # 保存结果
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 转录完成: {output_path}")
    print(f"   语言: {transcript['language']}")
    print(f"   时长: {transcript['duration']:.1f} 秒")
    print(f"   段落数: {len(transcript['segments'])}")

    # 清理临时音频文件
    if input_path.suffix.lower() not in audio_exts:
        Path(audio_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
