# 更新日志

所有重要变更记录于此。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [1.1.0] - 2026-10-20

### 新增

- 首个公开版本。
- 在 `on_llm_request` 里把非「管理员私聊」会话的受限工具直接摘掉
- 用框架原生 `remove_tool`，不改核心
- 优先级 100（早于记忆类插件），后续插件看到的是裁剪后的工具表
- 支持前缀通配：`browser_*` 一次匹配全部浏览器工具

