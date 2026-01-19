## Refactor skill

## `<command>` 示例
最好放到一个单独的py文件上，要求能够方便的移植到其他项目使用，且上层调用和实现足够方便。
比如上报metric，存tags需要的字段到flask.g，取字段等函数都放到同一个类上，作为类的方法。

## `<git_commit>` 示例（注意：用户要取想要分析的commit的上一个commit）
973a21b1


## Quick start
1. Confirm `<git_commit>` 和 `<command>` with the user.
2. 执行任务： 分析git commit `<git_commit>`到HEAD的代码，以最强大脑的视角做一个做一个重构（高内聚，易于上层调用，可读性高，可维护性高）。 
还需要满足以下要求：`<command>`



