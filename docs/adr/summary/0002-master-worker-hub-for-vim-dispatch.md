# ADR-0002 摘要：Master/Worker 模式解决多实例 Vim 反向查找分发

## 问题
ADR-0001 多实例部署后，Vim 只能连一个 Socket.IO 端口，无法收到其他 workspace 的反向查找结果。

## 关键发现
`pdf_server.py` 从一开始就被设计成两部分：Hub（管理 Vim 连接、转发结果）和 Worker（服务浏览器、SyncTeX 查找）。这是原作者为多实例扩展预留的架构。

## 决策
引入 master/worker 模式：
- `config.ini` 指定一个 workspace 为 master
- Master 实例运行 Hub + Worker，Vim 连这里
- Worker 实例只运行 Worker，反向查找结果 HTTP POST 转发到 master
- Master 收到后通过 Socket.IO broadcast 给 Vim

## 改动范围
- `config.ini`：加 `[server] master = <name>`
- `pdf_server.py`：`create_app` 加 `is_master` 参数，条件启用 Hub；worker 加 HTTP 转发逻辑

## 不需要改的
Vim 客户端、前端 JS、nginx、compile_and_sync.sh、synctex_tool.py——全部零改动。

## 向后兼容
不配置 master 时默认 `is_master=True`，单实例行为完全不变。
