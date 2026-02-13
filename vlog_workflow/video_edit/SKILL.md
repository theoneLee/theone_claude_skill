---
name: vlog_video_edit
description: 对录制的视频进行智能剪辑，去除重复和说错的内容，保持通顺自然
---

# Vlog Video Edit Skill

对用户录制的 vlog 视频进行智能剪辑：通过语音识别对比口播稿，自动标记需要剪辑的片段，经用户确认后执行精确剪切。

## 输入

- 原始视频文件路径（`raw.mp4`，支持 MP4/MOV 等常见格式）
- 口播稿文件路径（`speech.md`，用于对比参考）
- 特殊剪辑要求（可选）

## 前置条件

```bash
# 确保 speaches Docker 服务已启动
curl http://localhost:8000/v1/models
# 确保 ffmpeg 已安装
ffmpeg -version
```

## 核心流程

### Step 1: 语音识别（转录）

从视频中提取音频，调用 speaches API 进行语音识别：

```bash
python3 scripts/transcribe.py \
  --input ~/vlog_projects/{project}/raw.mp4 \
  --output ~/vlog_projects/{project}/transcript.json \
  --api-url http://localhost:8000
```

输出 `transcript.json` 包含带时间戳的逐段文字。

### Step 2: AI 智能分析（由 Agent 执行）

Agent 读取 `transcript.json` 和 `speech.md`，进行对比分析：

1. **对齐口播稿和实际录音**：找出两者的对应关系
2. **标记需剪辑的片段**：
   - 🔴 **重复内容**：同一段内容说了多次，保留最好的一次
   - 🔴 **说错/卡壳**：明显的口误或停顿过长
   - 🟡 **多余口头禅**：过于频繁的"嗯"、"那个"
3. **保留自然过渡**：
   - ✅ 保留必要的语气词（适量的"嗯"、"啊"、"这个"）
   - ✅ 保留章节间的自然过渡和停顿
   - ✅ 保留情感表达（笑声、感叹等）

### Step 3: 生成剪辑方案

Agent 生成 `cut_plan.json`，格式如下：

```json
{
  "keep_segments": [
    {"start": 0.0, "end": 45.2, "note": "开场白，表现自然"},
    {"start": 48.5, "end": 120.3, "note": "第一部分正文"},
    {"start": 125.0, "end": 180.0, "note": "第二部分，跳过了 120.3-125.0 的卡壳"}
  ],
  "removed_segments": [
    {"start": 45.2, "end": 48.5, "reason": "重复了开场白最后一句"},
    {"start": 120.3, "end": 125.0, "reason": "卡壳停顿 5 秒"}
  ]
}
```

### Step 4: 用户确认

向用户展示剪辑方案：
- 列出所有要删除的片段及原因
- 告知预计剪辑后时长
- 等待用户确认或调整

### Step 5: 执行剪辑

```bash
python3 scripts/cut_video.py \
  --input ~/vlog_projects/{project}/raw.mp4 \
  --plan ~/vlog_projects/{project}/cut_plan.json \
  --output ~/vlog_projects/{project}/edited.mp4
```

## 剪辑原则

### 必须剪掉

- 完全重复的段落（保留表现最好的一次）
- 明显的口误后重新开始的部分
- 超过 3 秒的无意义停顿

### 谨慎保留

- 短暂的思考停顿（1-2 秒）→ 保留，显得自然
- 偶尔的"嗯"、"那个" → 保留，避免机器感
- 语气加重、情感表达 → 一定保留
- 章节过渡处的自然停顿 → 保留

### 剪辑技巧

- **剪在语句间隙**：在句子的自然停顿处剪切，而非句中
- **保留呼吸音**：不要把呼吸声也剪掉，会显得不自然
- **前后 buffer**：每个保留片段前后各留 0.1-0.3 秒缓冲

## 输出

- 剪辑后的视频：`~/vlog_projects/{project}/edited.mp4`
- 剪辑报告：删除了哪些部分、原因、前后时长对比
