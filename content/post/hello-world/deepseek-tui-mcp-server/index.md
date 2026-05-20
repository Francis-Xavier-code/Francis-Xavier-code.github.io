---
title: DeepSeek TUI MCP Server 制作指南
date: 2026-05-20
slug: deepseek-tui-mcp-server
description: 制作deepseek-tui的mcp工具，以余额查询mcp为例
image: /img/deepseeklogo.jpg
categories:
  - 技术
  - 随笔
tags:
  - deepseek
  - ai
draft: false
---
# DeepSeek TUI MCP Server 制作指南

以 `ds-balance-mcp` 为例，说明如何为 DeepSeek TUI 制作一个 MCP Server。

## 架构概览

```text
DeepSeek TUI (MCP Host)          MCP Server (独立进程)
        │                              │
        │────  stdin (JSON-RPC) ──────→│
        │                              │
        │←──── stdout (JSON-RPC) ──────│
        │                              │
        │  python3 /path/to/server.py  │
```

- **传输层**：stdio，每行一个 JSON 对象
- **协议层**：JSON-RPC 2.0
- **注册层**：`~/.deepseek/mcp.json`

---

## 最简实现（3 个步骤）

### 步骤 1：实现 MCP 协议的核心方法

必须实现三个方法：

| 方法 | 作用 | 何时调用 |
|------|------|----------|
| `initialize` | 握手，声明协议版本和能力 | Server 启动后立即调用 |
| `tools/list` | 列出所有可用工具 | Initialize 之后 |
| `tools/call` | 执行具体工具 | 用户触发工具调用时 |

```python
def handle(req):
    mid = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    # ① 握手 —— 声明能力
    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": mid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "my-server", "version": "1.0.0"}
            }
        }

    # ② 列出工具 —— TUI 会据此生成 mcp_<server>_<tool> 工具
    if method == "tools/list":
        return {
            "jsonrpc": "2.0", "id": mid,
            "result": {
                "tools": [
                    {
                        "name": "hello",
                        "description": "打招呼，返回一句问候",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "要问候的名字"
                                }
                            },
                            "required": []
                        }
                    }
                ]
            }
        }

    # ③ 执行工具 —— 核心业务逻辑
    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "hello":
            name = arguments.get("name", "World")
            return {
                "jsonrpc": "2.0", "id": mid,
                "result": {
                    "content": [{"type": "text", "text": f"Hello, {name}!"}]
                }
            }

        # 未知工具返回错误
        return {
            "jsonrpc": "2.0", "id": mid,
            "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
        }

    # 未知方法返回错误
    return {
        "jsonrpc": "2.0", "id": mid,
        "error": {"code": -32601, "message": f"Unknown method: {method}"}
    }
```

### 步骤 2：写 stdio 主循环

```python
def main():
    # 可选：启动日志写到 stderr，不污染 stdout
    sys.stderr.write("my-server: ready\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            continue
        except (BrokenPipeError, EOFError):
            break
```

核心逻辑：**读一行 → 处理 → 写一行**。

### 步骤 3：在 `mcp.json` 中注册

编辑 `~/.deepseek/mcp.json`：

```json
{
  "servers": {
    "my-server": {
      "command": "python3",
      "args": ["/root/my-mcp-server.py"],
      "env": {},
      "enabled": true,
      "enabled_tools": [],
      "disabled_tools": []
    }
  }
}
```

| 字段 | 说明 |
|------|------|
| `command` | 启动命令 |
| `args` | 命令行参数 |
| `env` | 环境变量（可选） |
| `enabled` | 是否启用 |
| `enabled_tools` | 白名单（空=全部启用） |
| `disabled_tools` | 黑名单 |

重启 TUI 后会自动启动 Server 进程，工具名格式为 `mcp_<server名>_<工具名>`，例如 `mcp_my-server_hello`。

---

## 完整模板

以下是一个带错误处理的完整 Python MCP Server 模板：

```python
#!/usr/bin/env python3
"""MCP stdio server 模板"""
import sys
import json

def handle(req):
    mid = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    # 必须处理的协议方法
    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": mid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "my-server", "version": "1.0.0"}
            }
        }

    if method == "notifications/initialized":
        return None

    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}

    if method == "tools/list":
        return {
            "jsonrpc": "2.0", "id": mid,
            "result": {
                "tools": [
                    {
                        "name": "hello",
                        "description": "打招呼",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "名字"
                                }
                            }
                        }
                    }
                ]
            }
        }

    if method == "tools/call":
        tool = params.get("name")
        args = params.get("arguments", {})

        if tool == "hello":
            name = args.get("name", "World")
            return {
                "jsonrpc": "2.0", "id": mid,
                "result": {
                    "content": [{"type": "text", "text": f"Hello, {name}!"}]
                }
            }

        return {
            "jsonrpc": "2.0", "id": mid,
            "error": {"code": -32601, "message": f"Unknown tool: {tool}"}
        }

    return {
        "jsonrpc": "2.0", "id": mid,
        "error": {"code": -32601, "message": f"Unknown method: {method}"}
    }

def main():
    sys.stderr.write("my-server: ready\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            continue
        except (BrokenPipeError, EOFError):
            break

if __name__ == "__main__":
    main()
```

---

## ds-balance-mcp 实战分析

实际部署的 `ds-balance-mcp` 提供了两个工具：

| 工具名 | 功能 | 实现方式 |
|--------|------|----------|
| `check_balance` | 查询 DeepSeek API 余额 | HTTP GET `api.deepseek.com/user/balance`，从 `config.toml` 读取 API Key |
| `check_token_usage` | 查看当前会话 Token 用量 | 读取 `~/.deepseek/sessions/` 下最新的 JSON 会话文件 |

### `tools/list` 返回的工具定义

```json
{
    "tools": [
        {
            "name": "check_balance",
            "description": "查询 DeepSeek API 账户余额（单位：CNY）",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "check_token_usage",
            "description": "查看当前会话的 Token 用量、费用和模型信息",
            "inputSchema": {"type": "object", "properties": {}}
        }
    ]
}
```

### `tools/call` 返回的结果格式

```json
// 成功
{
    "jsonrpc": "2.0", "id": "mid",
    "result": {
        "content": [{"type": "text", "text": "结果文本（JSON 或纯文本）"}]
    }
}

// 失败
{
    "jsonrpc": "2.0", "id": "mid",
    "error": {"code": -32000, "message": "错误描述"}
}
```

---

## 使用 Skill 快速搭建

DeepSeek TUI 内置了 `mcp-builder` 技能，可以辅助设计、构建和调试 MCP Server：

```bash
/skill mcp-builder
```

该 Skill 支持 stdio 和 HTTP/SSE 两种传输方式。

---

## 关键点总结

1. **传输**：stdio，一行一个 JSON-RPC 消息
2. **协议**：必须实现 `initialize`、`tools/list`、`tools/call`
3. **注册**：在 `~/.deepseek/mcp.json` 的 `servers` 中添加配置
4. **日志**：打到 stderr，不要污染 stdout
5. **结果**：`content` 数组，每项 `{"type": "text", "text": "..."}`
6. **工具名**：TUI 自动加前缀 `mcp_<server名>_<工具名>`