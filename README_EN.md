# Tool Guard: restrict dangerous tools to admin private chat

> AstrBot plugin · Trim tool availability per session, no core patches

## The problem

The built-in `future_task` lets the model schedule itself and post into a session later, with no permission gate — anyone in a group can trigger it.

That path bypasses the whole pipeline, so group-muting plugins can't stop it.

Scheduled posting is one of the most obvious bot signatures.

## Features

- Removes restricted tools for non-admin sessions in `on_llm_request`
- Uses the native `remove_tool`, no core changes
- Priority 100 — later plugins see the trimmed tool table
- Prefix wildcards: `browser_*` matches all browser tools

## Install

### Option 1: Plugin marketplace (recommended)

Search "工具守卫" in the AstrBot WebUI plugin marketplace.

### Option 2: Download from Releases

Grab the zip from [Releases](../../releases), then WebUI → Plugins → Upload.

### Option 3: Clone manually

```bash
cd AstrBot/data/plugins
git clone https://github.com/RandyLuaW/astrbot_plugin_tool_guard.git
```

No extra Python dependencies.

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `enabled` | bool | `true` | See Chinese README |
| `restricted_tools` | list | `['future_task']` | See Chinese README |
| `allow_admin_private` | bool | `true` | See Chinese README |
| `log_once` | bool | `true` | See Chinese README |

## Notes

- Defaults to `future_task` only
- `allow_admin_private=false` disables the tools for everyone

## License

MIT
