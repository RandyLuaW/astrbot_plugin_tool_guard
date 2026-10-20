# -*- coding: utf-8 -*-
"""工具守卫：按会话裁剪危险工具。

为什么需要
----------
    AstrBot 内置的 `future_task` 能让她定时唤醒自己，到点直接往原会话发消息。
    但 `create` 没有任何权限门槛——群里任何人都能让她建任务，而这条路径
    绕过整条 pipeline（`_woke_main_agent` 直接投递），群屏蔽拦不住。
    定时发言是最典型的机器行为特征，风控期不能开这个口子。

做法
----
    on_llm_request 钩子里，非「管理员私聊」的会话直接
    `req.func_tool.remove_tool(name)`。框架原生支持，不改 AstrBot 核心。

优先级取 100（早于 iris 的 0），保证后面的插件看到的是裁剪后的工具表。
"""

from __future__ import annotations

from typing import Any

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

PLUGIN_NAME = "astrbot_plugin_tool_guard"

DEFAULT_CONFIG = {
    "enabled": True,
    "restricted_tools": ["future_task"],
    "allow_admin_private": True,
    "log_once": True,
}

# 必须早于其它 on_llm_request 钩子，让后续插件看到裁剪后的工具表
HOOK_PRIORITY = 100


class ToolGuardPlugin(Star):
    def __init__(self, context: Context, config: Any = None):
        super().__init__(context)
        self.config = dict(DEFAULT_CONFIG)
        if isinstance(config, dict):
            self.config.update({k: v for k, v in config.items() if k in DEFAULT_CONFIG})
        self._logged: set[str] = set()

    async def initialize(self) -> None:
        names = self._names()
        logger.info(f"[tool-guard] 就绪，受限工具 {names or '（未配置）'}")

    async def terminate(self) -> None:
        pass

    def _cfg(self, key: str) -> Any:
        return self.config.get(key, DEFAULT_CONFIG.get(key))

    def _names(self) -> list[str]:
        raw = self._cfg("restricted_tools") or []
        if isinstance(raw, str):
            raw = [x.strip() for x in raw.replace("，", ",").split(",")]
        return [str(x).strip() for x in raw if str(x).strip()]

    def _match(self, tool_name: str, patterns: list[str]) -> bool:
        """精确名或前缀通配（`browser_*`）匹配。"""
        for p in patterns:
            if p.endswith("*"):
                if tool_name.startswith(p[:-1]):
                    return True
            elif tool_name == p:
                return True
        return False

    def _allowed(self, event: AstrMessageEvent) -> bool:
        """管理员私聊放行，其余一律受限。"""
        if not self._cfg("allow_admin_private"):
            return False
        try:
            if event.is_admin() is not True:
                return False
            return event.is_private_chat() is True
        except Exception:
            return False

    @filter.on_llm_request(priority=HOOK_PRIORITY)
    async def guard_tools(self, event: AstrMessageEvent, req: Any) -> None:
        if not self._cfg("enabled"):
            return
        if self._allowed(event):
            return

        tool_set = getattr(req, "func_tool", None)
        if tool_set is None or not hasattr(tool_set, "remove_tool"):
            return

        removed = []
        patterns = self._names()
        present = [
            str(getattr(t, "name", "") or "")
            for t in getattr(tool_set, "tools", [])
        ]
        for name in present:
            if not name or not self._match(name, patterns):
                continue
            try:
                tool_set.remove_tool(name)
                removed.append(name)
            except Exception:
                continue

        if removed and self._cfg("log_once"):
            umo = str(getattr(event, "unified_msg_origin", "") or "")
            if umo not in self._logged:
                self._logged.add(umo)
                logger.info(f"[tool-guard] {umo} 非管理员私聊，已摘除 {removed}")
