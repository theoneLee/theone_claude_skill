
1. AGENTS.md 放入到这个：~/.codex/AGENTS.md （这个会使得 codex 默认使用这个 AGENTS.md）

2. codex 开启 sub-agents：通过 /experimental 然后勾上 Sub-agents

3. ~/.codex/config.toml 下配置：collab = true 和 parallel = true (关注config.toml文件)


config.toml 核心参数,关注features下的参数
```
disable_response_storage = true
model_provider = "cch"
network_access = true
sandbox_mode = "workspace-write"
experimental_use_rmcp_client = true
model = "gpt-5.3-codex"
model_reasoning_effort = "xhigh"
personality = "pragmatic"
web_search = "live"

[features]
plan_tool = true
view_image_tool = true
streamable_shell = false
rmcp_client = true
skills = true
parallel = true
unified_exec = true
shell_snapshot = true
collab = true
steer = true
```

这个模式下，我同时3 个项目进度优化明显，副作用也很明显一天干了 100 刀+，好在 codex 比较便宜。

ref：
https://linux.do/t/topic/1603762