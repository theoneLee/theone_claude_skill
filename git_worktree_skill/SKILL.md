---
name: git_worktree_skill
description: 使用 git worktree 管理并行开发工作区的技能。它允许 agent 在独立的工作目录中处理不同的分支，避免在主工作区产生冲突，并支持高效的多任务并行。
---

# Git Worktree Skill

该技能旨在帮助 agent 合理利用 `git worktree` 创建独立的工作区，从而支持多个 agent 或多个任务并行开发，避免代码冲突和工作区混乱。

## 核心任务

1. **评估需求**：当需要并行处理多个任务（如一个 agent 在做重构，另一个在修 bug）时，自动评估是否需要创建新工作区。
2. **工作区创建**：
    - 检查目标分支是否已存在。
    - 使用 `git worktree add <path> <branch>` 创建新工作区。建议路径格式为 `../worktrees/<branch_name>` 或在项目根目录外的专用目录。
3. **环境准备**：在新工作区中执行必要的初始化命令（如 `npm install`、`go mod download` 或 `uv sync`），确保开发环境独立且可用。
4. **状态同步**：在任务完成后，确保代码已提交并推送到远端。
5. **清理资源**：任务彻底结束并确认代码合入后，使用 `git worktree remove <path>` 清理工作区及其相关文件，保持系统整洁。

## 操作流程示例

### 1. 创建并切入新工作区

用户要求： "为一个新的 feature `feat-login` 创建一个独立的工作区进行开发。"

执行逻辑：
1. 运行 `git worktree add ../robotaxi-feat-login -b feat-login`。
2. 进入新路径：`cd ../robotaxi-feat-login`。
3. 执行初始化：`uv sync` (如果是 Python 项目) 或 `go mod tidy` (如果是 Go 项目)。

### 2. 列出当前所有工作区

运行 `git worktree list` 查看所有活跃的工作区及其对应分支。

### 3. 清理已完成的工作区

运行 `git worktree remove ../robotaxi-feat-login`。如果存在未提交的更改，需先处理或使用 `--force`（慎用）。

## 注意事项

- **分支冲突**：Git 不允许在两个不同的工作区同时 checkout 同一个分支。
- **路径管理**：确保工作区路径在项目根目录之外，以避免被误包含在 Git 管理中或引起依赖扫描问题。
- **资源消耗**：大量的工作区可能会占用较多磁盘空间，尤其是包含 `node_modules` 或庞大依赖的项目，及时清理非常重要。
- **DB/缓存隔离**：如果项目依赖本地数据库或缓存，需注意并行工作区可能共享这些资源，必要时需配置独立的环境变量。
