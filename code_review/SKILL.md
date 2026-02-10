---
name: code_review
description: 用于代码审查的 Skill，支持通用准则以及 Python 和 Go 的专项审查。
---




# Code Review Skill

本 Skill 用于对代码进行深度审查，特别是针对 `<git_commit>` 到 `HEAD` 的git变更的代码。审查过程应当关注代码质量、逻辑正确性、性能以及架构设计。

## 审查准则 (Review Guidelines)

### 1. 通用准则 (General)
*   **命名规范**: 
    *   禁止使用 `flag`、`data`、`info` 等这类业务意义含糊且过于通用的变量/函数命名方式。
    *   变量名应能反映其存储的内容，函数名应能反映其执行的动作。
*   **逻辑正确性与性能**:
    *   重点审查边界条件处理、异常流转。
    *   检查是否存在不必要的循环、重复的 IO 操作或低效的算法。
    *   检查 jeff dean 提到的了解每个操作的性能开销的数量级。比如cpu操作是ns级别，io操作是ms级别，代码中是否存在在大量cpu操作的地方（需要高性能时），引入大量io操作，导致性能下降。
*   **优先使用项目内已经实现的工具函数**:
    *   项目内已经实现了一些工具函数，优先使用这些工具函数，避免重复造轮子。
*   **DRY 原则 (Don't Repeat Yourself)**:
    *   核查代码重复情况，对于超过两次出现的相似逻辑，需考虑提取为公共函数或组件。
*   **单一职责原则 (Single Responsibility Principle)**:
    *   核查代码是否职责单一，一个函数只做一件事。做好目录分层，符合高内聚的设计原则。
*   **开闭原则 (Open/Closed Principle) （次要）**:
    *   遵循面向对象设计原则，对扩展开放，对修改关闭。易于拓展
*   **设计模式与架构 (次要)**:
    *   核查业务流程是否过于臃肿，是否可以抽象。
    *   推荐使用“模板方法”等设计模式来增强代码的拓展性。给出如何抽象的建议。


### 2. Python 专项准则 (Python Specific)
*   **Pythonic**: 优先使用列表推导式 (List Comprehensions)、生成器 (Generators)。
*   **资源管理**: 确保使用 `with` 语句管理文件、网络连接等资源。
*   **异步处理**: 若使用 `asyncio`，审查是否存在阻塞事件循环的操作。

### 3. Go 专项准则 (Go Specific)
*   **错误处理**: 坚持 "Check errors early and return early"。禁止忽略错误返回。
*   **并发安全**: 
    *   检查 Goroutine 是否有泄露风险。
    *   检查竞态条件，检查对共享变量的访问是否使用了互斥锁 (Mutex) 或通过 Channel 同步。
    *   检查死锁风险。
    *   etc...
*   **接口设计**: 崇尚小接口 (Small interfaces)。
*   **性能优化**: 减少不必要的内存分配，注意 `slice` 的扩容成本。


## Severity Levels

| Level | Name | Description | Action |
|-------|------|-------------|--------|
| **P0** | Critical | Security vulnerability, data loss risk, correctness bug | Must block merge |
| **P1** | High | Logic error, significant SOLID violation, performance regression | Should fix before merge |
| **P2** | Medium | Code smell, maintainability concern, minor SOLID violation | Fix in this PR or create follow-up |
| **P3** | Low | Style, naming, minor suggestion | Optional improvement |

## workflow/执行步骤
1. 跟用户确认变量: 
    * 在审查前，需要和用户确认 `<git_commit>`变量是多少（注意：用户要取想要分析的commit的上一个commit）。 示例：973a21b1


*   **代码lint和单测**:
    *   在正式review前，执行make lint，检查代码是否符合代码规范。
    *   在正式review前，执行make test，检查是否通过单测。
2. 利用「审查准则」对代码进行审查。
3. 按照「交互与输出规范」分点，分优先级进行输出审查意见，推荐修改方式/思路
4. 询问用户是否需要针对哪个问题进行修改？默认使用review的修改建议进行修改。用户可以补充自己的修改建议。 用户回复示例：针对case1, case3 进行修改，其中case3还需要增加xxx能力。


**Important**: Do NOT implement any changes until user explicitly confirms. This is a review-first workflow.


## 交互与输出规范 (Interaction)

```markdown
## Code Review Summary

## 被review 的代码实现了什么功能
xxxxx

## suggest git commit message
xxxxx（英文输出，尽量简短）

## 问题列表

### P0 - Critical
(none or list)

### P1 - High
- case1 **[file:line]** 问题标题
  - 问题描述
  - 修复建议
- case2 **[file:line]** 问题标题
  - 问题描述
  - 修复建议
### P2 - Medium
- case3 **[file:line]** 问题标题
  - 问题描述
  - 修复建议

### P3 - Low
- case4 **[file:line]** 问题标题
  - 问题描述
  - 修复建议


```