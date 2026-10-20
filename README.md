# 工具守卫：危险工具只对管理员私聊开放

> AstrBot 插件 · 危险工具只对管理员私聊开放

## 它解决什么问题

框架内置的 `future_task` 能让模型定时唤醒自己，到点直接往原会话发消息，但创建任务没有任何权限门槛——群里任何人都能触发。

而这条路径绕过整条 pipeline（直接投递），群屏蔽类插件拦不住。

定时发言是最典型的机器行为特征，风控期不能开这个口子。

## 功能

- 在 `on_llm_request` 里把非「管理员私聊」会话的受限工具直接摘掉
- 用框架原生 `remove_tool`，不改核心
- 优先级 100（早于记忆类插件），后续插件看到的是裁剪后的工具表
- 支持前缀通配：`browser_*` 一次匹配全部浏览器工具

## 工作机制

on_llm_request(priority=100)
    ├─ 会话是管理员私聊 → 放行
    └─ 其他 → 对 restricted_tools 逐个 remove_tool
                （支持 `前缀*` 通配）

摘除只作用于本次请求，不动插件注册表。

## 安装

### 方式一：插件市场（推荐）

WebUI 插件市场搜索「工具守卫」。

### 方式二：Releases 下载

从 [Releases](../../releases) 下载 zip，WebUI → 插件 → 上传安装。

### 方式三：手动克隆

```bash
cd AstrBot/data/plugins
git clone https://github.com/RandyLuaW/astrbot_plugin_tool_guard.git
```

无额外 Python 依赖。

## 配置项

| 键 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `enabled` | bool | `true` | 启用工具守卫。关闭后所有会话都能用受限工具。 |
| `restricted_tools` | list | `['future_task']` | 要限制的工具名列表。只有管理员私聊能用这些工具。支持 `前缀*` 通配，例如 `browser_*` 会匹配全部浏览器工具。 |
| `allow_admin_private` | bool | `true` | 管理员私聊是否放行。关闭后等于所有人都不能用。 |
| `log_once` | bool | `true` | 每个会话只记一次摘除日志，避免刷屏。 |

## 注意事项

- 默认只限 `future_task`；要连浏览器一起限，加 `browser_*`
- `allow_admin_private=false` 等于所有人都不能用

## License

MIT
