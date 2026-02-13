---
name: vlog_workflow
description: Vlog节目录制剪辑自动化流程，协调手写稿→PPT→口播稿→录制→剪辑→字幕的完整流程
---

# Vlog Workflow Skill

本 Skill 协调 vlog 节目的完整制作流程。可以从任意步骤开始执行。

## 前置依赖

执行任何步骤前，先检查以下依赖：

```bash
# 1. Docker（speaches 语音识别服务需要）
docker --version

# 2. ffmpeg（视频剪辑和字幕烧录需要）
ffmpeg -version

# 3. python-pptx（PPT 生成需要）
pip show python-pptx || pip install python-pptx
```

## 工作目录约定

所有项目文件统一放在 `~/vlog_projects/{project_name}/` 下：

```
~/vlog_projects/{project_name}/
├── draft.md          # 用户手写稿
├── speech.md         # AI 生成的口播稿
├── slides.pptx       # AI 生成的 PPT
├── raw.mp4           # 用户录制的原始视频
├── transcript.json   # Whisper 语音识别结果
├── cut_plan.json     # 剪辑方案（保留区间列表）
├── edited.mp4        # 剪辑后的视频
├── subtitle.srt      # 字幕文件
└── final.mp4         # 最终带字幕的视频
```

## 完整流程

### Step 1: 收集手写稿

1. 询问用户本期 vlog 的主题/项目名称
2. 创建工作目录：`mkdir -p ~/vlog_projects/{project_name}`
3. 询问用户手写稿内容，保存为 `draft.md`

### Step 2: 生成 PPT

调用 `script_to_ppt` 子 skill：
- 输入：`draft.md`
- 输出：`slides.pptx`
- 用户确认 PPT 内容后进入下一步

### Step 3: 生成口播稿

调用 `script_to_speech` 子 skill：
- 输入：`draft.md`
- 输出：`speech.md`（含 PPT 页码对应关系）
- 用户确认口播稿后进入下一步

### Step 4: 用户录制视频

1. 告知用户使用口播稿配合 PPT 进行录制
2. **向用户展示以下录制技巧**：
   - 🎯 **说错后停 2-3 秒再重来**：停顿产生静音区，AI 能精确识别"重来点"
   - 🎯 **重说时从整句开头重来**：不要只重说错的几个字，整段替换拼接更自然
   - 💡 **可以拍桌子/打响指标记错误**：音频尖峰帮助 AI 定位剪辑点
   - 💡 **章节切换时说一句"下一页"**：帮助 AI 对齐内容和 PPT 页码
   - 💡 **保持身体位置一致**：重说时不要大幅移动，避免画面跳跃
   - 💡 **开头结尾各多录 5 秒**：预留剪辑缓冲空间
3. 提示：录制时不必追求一遍过，说错/卡壳可以重来，后续 AI 会自动剪辑
4. 等待用户提供录制好的视频文件，复制或移动到 `raw.mp4`

### Step 5: 视频剪辑

调用 `video_edit` 子 skill：
- 输入：`raw.mp4` + `speech.md`（口播稿作为参考）
- 流程：语音识别 → AI 标记剪辑点 → 用户确认 → 执行剪辑
- 输出：`edited.mp4`

### Step 6: 字幕配置

调用 `subtitle` 子 skill：
- 输入：`edited.mp4`
- 流程：语音识别 → 生成 SRT → 可选烧录到视频
- 输出：`subtitle.srt` + `final.mp4`

## 启动 Whisper 语音识别服务

Step 5 和 Step 6 依赖 speaches（faster-whisper Docker 服务）。

**首次执行时询问用户**：你希望使用 CPU 模式（M1 Mac）还是 GPU 模式（AMD RX 7600）？
- CPU 模式：在 M1 Mac 本地运行，速度较慢但无需额外配置
- GPU 模式：通过 AMD RX 7600 + ROCm 加速，速度提升 3-5 倍，需要在装有显卡的机器上运行 Docker

### CPU 模式（M1 Mac）

```bash
docker compose -f /path/to/vlog_workflow/docker-compose.yml --profile cpu up -d
```

### GPU 模式（AMD RX 7600 / ROCm）

```bash
docker compose -f /path/to/vlog_workflow/docker-compose.yml --profile gpu up -d
```

服务启动后可通过 `http://localhost:8000` 访问 OpenAI 兼容 API。

## Sub Skills

| Skill | 功能 | 入口 |
|-------|------|------|
| script_to_ppt | 手写稿 → PPT | `script_to_ppt/SKILL.md` |
| script_to_speech | 手写稿 → 口播稿 | `script_to_speech/SKILL.md` |
| video_edit | 视频剪辑 | `video_edit/SKILL.md` |
| subtitle | 字幕配置 | `subtitle/SKILL.md` |

## 重要提示

- 每个步骤都需要用户确认后再进行下一步
- 可以通过指定步骤编号从任意步骤开始（如"从 Step 5 开始"）
- 视频文件较大，确保磁盘空间充足
- 剪辑和字幕都依赖 speaches 服务，首次使用需要下载模型（约 3GB）
