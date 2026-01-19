# SKILL: Git Agentic Workflow (No-Script Version)

## 概述
本 Skill 指导 Claude 使用原生的 Git 命令完成从 feat 到 pre 分支的标准化发布流程。

## 核心 SOP 流程
当用户要求“发布到 pre”或“同步分支”时，请严格按顺序执行以下原子操作：

### 变量定义
- `<main_branch>`：主干分支名，通常为 `master` 或 `main`。
- `<feature_branch>`：用户指定的功能分支名；若未指定，默认使用当前分支名。

### 步骤 0：确认分支基线 (Branch Baseline)
- **动作**：
  - 先确认主干分支名称：`git symbolic-ref --short refs/remotes/origin/HEAD`。
  - 若返回 `origin/main`，用 `main` 替代文档中的 `master`；否则沿用 `master`。
  - 由用户指定功能分支名，本文以 `<feature_branch>` 代指（如 `feat/xxx`）。若未指定，默认使用当前分支名。
  - 确认当前操作分支为 `<feature_branch>`，如不是则先切换到 `<feature_branch>`。

### 步骤 1：环境保全 (Stash)
- **检查状态**：执行 `git status`。
- **动作**：若工作区不干净，执行 `git stash push -u -m "Claude-Auto-Stash-<DATE>"`。

### 步骤 2：同步 Master (Sync)
- **动作**：切换到 `<feature_branch>` 分支，执行 `git fetch --prune origin <main_branch>`，然后执行 `git merge origin/<main_branch>`。
- **冲突处理**：
    - 若发生冲突，**禁止**盲目合并。
    - 运行 `git log -n 5 --graph --oneline` 分析主干与 feat 的意图。
    - 读取冲突文件，根据业务逻辑（优先保留主干基础设施改动，织入 feat 业务改动）修复代码。
    - 修复后执行 `git add` 并 `git commit`。

### 步骤 3：恢复现场 (Pop)
- **动作**：执行 `git stash pop`。若有冲突，参照“步骤 2”的逻辑手动解决并 commit。

### 步骤 4：重建 Pre 分支 (Rebuild)
- **动作**：
    1. `git branch -D pre` (若本地存在)。
    2. `git checkout -b pre origin/<main_branch>`。

### 步骤 5：远程备份与清理 (Remote Backup)
- **动作**：
    1. 检查远程是否存在 `pre`。
    2. 若存在，先 `git fetch --prune origin`，再执行 `git push origin origin/pre:refs/heads/pre_$(date +%Y%m%d)`。
    3. **确认备份成功后**，再执行 `git push origin --delete pre`。

### 步骤 6：最终合并与推送 (Final Merge)
- **动作**：
    1. 将 `<feature_branch>` 合并到当前 `pre` 分支。
    2. 执行 `git push origin pre`。

## 异常处理守则
- **自愈能力**：如果在任何一步失败，请分析错误信息，尝试修复。如果无法自愈（如权限问题），请向用户报告具体进度。
- **记忆点**：若任务中断后重启，请先扫描当前分支状态和 `git stash list`，从中断的环节无缝衔接，不要重复执行已完成的步骤。

## 复杂冲突处理清单（补充）
- **冲突定位**：`git status`，`git diff --name-only --diff-filter=U`。
- **细粒度冲突**：`git checkout --conflict=merge <file>` 或手动对比 `<<<<<<<` 块。
- **快速择一**：`git checkout --ours/--theirs <file>`（只在明确选择一方时使用）。
- **重命名/删除冲突**：优先确认最终文件路径，必要时手动移动后 `git add -A`。
- **二进制冲突**：只能择一，需业务方确认来源。
- **工具辅助**：如配置了 `git mergetool`，可用于复杂冲突。
- **合并后验证**：至少运行目标模块的最小用例或 lint，确认无结构性回归。
