---
name: vlog_script_to_ppt
description: 将手写稿转换为图文并茂、颜色吸引眼球的PPT
---

# Vlog Script to PPT Skill

将用户的 Markdown 手写稿转换为视觉吸引力强的 PPT 演示文稿。

## 输入

- 手写稿文件路径（Markdown 格式的 `draft.md`）
- PPT 主题/标题
- 配色风格（可选，默认"科技蓝"）
- 期望页数（可选，默认根据内容自动决定）

## 配色方案

| 风格 | 主色 | 辅色 | 背景 | 适用场景 |
|------|------|------|------|----------|
| 科技蓝 | #1A73E8 | #34A853 | #FFFFFF | 技术/编程类 |
| 活力橙 | #FF6D00 | #FFD600 | #FFF8E1 | 生活/娱乐类 |
| 清新绿 | #00C853 | #00BFA5 | #E8F5E9 | 自然/健康类 |
| 深邃紫 | #6200EA | #AA00FF | #F3E5F5 | 创意/设计类 |
| 商务灰 | #37474F | #607D8B | #ECEFF1 | 商业/职场类 |

## 执行步骤

1. **读取手写稿**：解析 `draft.md`，提取标题和各段内容
2. **结构规划**：
   - 封面页（标题 + 副标题）
   - 目录页（如果内容较多）
   - 内容页（每页一个核心观点，文字简洁 + 关键词高亮）
   - 过渡页（章节之间的分隔）
   - 结尾页（感谢/互动引导）
3. **生成配图**：对每个内容页，使用 `generate_image` 工具生成与主题匹配的配图
4. **生成 PPT**：运行 `scripts/generate_ppt.py` 脚本
5. **用户确认**：告知用户 PPT 路径，让用户预览并提出修改意见

## 脚本使用

```bash
# 依赖安装
pip install python-pptx Pillow

# 生成 PPT
python3 scripts/generate_ppt.py \
  --input ~/vlog_projects/{project}/draft.md \
  --output ~/vlog_projects/{project}/slides.pptx \
  --title "节目标题" \
  --theme tech_blue
```

## 每页布局规则

- **文字**: 每页不超过 5 个要点，每个要点不超过 15 个字
- **字号**: 标题 36pt，正文 24pt，注释 18pt
- **图片**: 每页至少一张配图或图标，占页面 40% 面积
- **留白**: 四周留足边距，不让内容显得拥挤

## 适合口播的设计

- 内容按口播节奏分页，每页对应 30-60 秒的讲述
- 将页码标注在口播稿中，方便录制时翻页
- 使用动画效果（渐入）引导观众注意力

## 输出

- 生成的 PPT 文件路径：`~/vlog_projects/{project}/slides.pptx`
- 建议的演示时间
- 可调整的内容清单
