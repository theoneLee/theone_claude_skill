---
name: vlog_subtitle
description: 为剪辑后的视频自动生成并配置字幕
---

# Vlog Subtitle Skill

为视频自动生成字幕（通过语音识别）并可选烧录到视频中。

## 输入

- 视频文件路径（通常是剪辑后的 `edited.mp4`）
- 字幕样式偏好（可选，默认白色 + 黑色描边）

## 前置条件

```bash
# 确保 speaches Docker 服务已启动
curl http://localhost:8000/v1/models
# 确保 ffmpeg 已安装
ffmpeg -version
```

## 执行步骤

### Step 1: 语音识别

如果 video_edit 阶段已生成过 `transcript.json`（针对原始视频），则需要对剪辑后的视频**重新转录**，因为时间轴已变化：

```bash
python3 ../video_edit/scripts/transcribe.py \
  --input ~/vlog_projects/{project}/edited.mp4 \
  --output ~/vlog_projects/{project}/edited_transcript.json \
  --api-url http://localhost:8000
```

### Step 2: 生成 SRT 字幕

```bash
python3 scripts/generate_srt.py \
  --input ~/vlog_projects/{project}/edited_transcript.json \
  --output ~/vlog_projects/{project}/subtitle.srt
```

### Step 3: AI 校对（由 Agent 执行）

Agent 读取 `subtitle.srt` 和 `speech.md`（口播稿）进行校对：
- 修正语音识别的错别字
- 确认专有名词拼写正确
- 调整句子分割使其阅读自然
- 每行控制在 15-20 字以内

将校对后的内容重新写入 `subtitle.srt`。

### Step 4: 烧录字幕（可选）

```bash
python3 scripts/burn_subtitle.py \
  --input ~/vlog_projects/{project}/edited.mp4 \
  --subtitle ~/vlog_projects/{project}/subtitle.srt \
  --output ~/vlog_projects/{project}/final.mp4
```

## 字幕样式选项

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 字体 | Noto Sans CJK SC | 清晰易读的无衬线中文字体 |
| 字号 | 24 | 适合移动端观看 |
| 颜色 | 白色 | 在大多数画面上清晰 |
| 描边 | 黑色 2px | 确保在浅色背景上也能看清 |
| 位置 | 底部居中 | 标准字幕位置 |
| 边距 | 底部 40px | 避免被播放器控件遮挡 |

## 输出格式选择

- **SRT**（默认）：兼容性最好，所有播放器和平台都支持
- **ASS**：支持更多样式（字体、颜色、特效），适合 B 站等
- **内嵌字幕**：直接烧录到视频中，适合发布到不支持外挂字幕的平台

## 输出

- 字幕文件：`~/vlog_projects/{project}/subtitle.srt`
- 带字幕视频：`~/vlog_projects/{project}/final.mp4`（如选择烧录）
