# ADR-0002: Master/Worker Mode for Multi-Instance Vim Reverse Search Dispatch

## Status
Proposed

## Context

ADR-0001 parameterizes the static directory to enable multi-instance deployment (one pdf_server process per workspace, each on a separate port). This solves the browser-side problem: each browser connects to its own workspace's pdf_server through nginx path-prefix routing.

However, the **Vim editor client** connects via Socket.IO to receive `reverse_search_result` events. In a multi-instance topology, Vim would need to connect to every instance simultaneously to receive results from any workspace. This is architecturally broken:

1. Vim doesn't know how many instances exist or which ports they use
2. Backend ports are not directly accessible from Vim's network — nginx exposes a single host
3. Multiple simultaneous connections would create race conditions on reverse search results

### Pre-existing Design: Hub/Worker Separation

`pdf_server.py` was intentionally designed with two logical parts from the start, anticipating this expansion:

**Hub part** — manages Vim connections and dispatches results to Vim:
- `VimClient` class and `vim_clients` dict (L23-35)
- `connect`/`disconnect` handlers (L62-73)
- `task_result` handler (L75-77)
- `relay_reverse_search` broadcast (L79-86)
- `reverse_search_result` emit to all clients (L118-121)

**Worker part** — serves browser, handles PDF and SyncTeX:
- Forward search blueprint `/send_pdf_reload` (L57-60)
- `handle_reverse_search` — browser double-click → SyncTeX reverse lookup (L88-126)
- Index route, health check (L128-136)
- Static file serving (Flask static_folder)

This separation is the foundation for the multi-instance solution.

### Related Issue

`docs/issues/2026-04-04-140000/multi-instance-vim-dispatch.md` — documents the problem in detail, including nginx configuration and data flow analysis.

## Decision

**Introduce a master/worker mode**: one instance is designated as master and runs both Hub and Worker; all other instances run only Worker and forward reverse search results to the master.

### Topology

```
config.ini:
[workspaces]
static = 7777       ← master (runs Hub + Worker)
stafuk = 7771       ← worker only
stutuka = 7772      ← worker only

[server]
master = static     ← declares which workspace is master
```

```
pdf_server:7777 (master, "static")
  ├── Worker: serves browser, SyncTeX lookup
  └── Hub: manages Vim connections, receives forwarded results

pdf_server:7771 (worker, "stafuk")
  ├── Worker: serves browser, SyncTeX lookup
  └── On reverse_search_result → HTTP POST to :7777

pdf_server:7772 (worker, "stutuka")
  ├── Worker: serves browser, SyncTeX lookup
  └── On reverse_search_result → HTTP POST to :7777

Vim ──Socket.IO──→ :7777 (master only)
  └── Receives reverse_search_result from ALL workspaces
```

### How it works

**Master instance (port from `config.ini [workspaces][<master>]`):**
- Runs exactly as today — Hub part fully active
- Adds one new HTTP endpoint: `POST /hub/reverse_search_result` — receives forwarded results from worker instances and broadcasts via Socket.IO to Vim
- Vim connects here and only here

**Worker instances (all other ports):**
- Hub part disabled: `VimClient` management inactive, no direct `reverse_search_result` broadcast
- When `handle_reverse_search` (L88-126) computes a result, instead of `socketio.emit('reverse_search_result', ...)`, it does `HTTP POST` to `http://127.0.0.1:<master_port>/hub/reverse_search_result` with `{workspace, file, line}`
- The local browser still receives the result via its own Socket.IO (for editor bridge), but Vim gets it through the master

**Vim side:**
- Zero changes. Connects to master port as before. Receives `reverse_search_result` events carrying `{file, line}` with absolute paths — Vim doesn't need to know which workspace originated the result.

### Changes required

#### 1. `config.ini` — add master designation

```ini
[server]
master = static

[workspaces]
static = 7777
stafuk = 7771
stutuka = 7772
```

#### 2. `pdf_server.py` — conditional Hub activation

In `create_app()`, accept an `is_master` parameter:

- **If master:** register all existing Socket.IO handlers (connect, disconnect, relay, etc.) AND register new HTTP endpoint `POST /hub/reverse_search_result` that broadcasts received data via Socket.IO
- **If worker:** skip VimClient-related handlers. In `handle_reverse_search`, after computing the result, POST it to master instead of (or in addition to) local broadcast

The worker still does `socketio.emit('reverse_search_result', ...)` locally so the browser's editor bridge path continues to work. The HTTP POST to master is an additional action.

#### 3. `__main__` block — resolve master status

```python
master_name = config.get('server', 'master', fallback=None)
is_master = (master_name is None) or (dir_name == master_name)
app = create_app(static_dir=static_dir, is_master=is_master)
```

When `master` is not configured (single-instance deployment), `is_master=True` — backward compatible.

### No changes required

| Component | Why |
|-----------|-----|
| `synctex_tool.py` | Pure computation, no network awareness |
| `socketapp.py` | Per-process state, unaffected by master/worker distinction |
| `send_socket_message_to_pdfjs.py` | Forward search path, browser-only, unaffected |
| Frontend JS (all files) | Browser connects to its own workspace's pdf_server — no change |
| `compile_and_sync.sh` | Forward search path, targets its own workspace's port — no change |
| Vim client (channel.py) | Connects to master port as before — zero change |
| nginx config | Browser routing unchanged; Vim connects to master's existing path — no new route needed |

## Alternatives Considered

### A. Standalone Hub process

A separate process that pdf_server instances and Vim all connect to as clients.

Rejected because:
- Requires a new process, new codebase, new deployment concern
- pdf_server would need to become both Socket.IO server (for browser) and Socket.IO client (for hub) — significant complexity
- The Hub logic already exists inside pdf_server.py — extracting it to a separate process duplicates infrastructure
- One more thing to monitor, restart, and debug

### B. Vim connects to all instances simultaneously

Vim iterates over `config.ini [workspaces]` and opens Socket.IO connections to every port.

Rejected because:
- Backend ports not directly accessible from Vim's network (nginx fronts them)
- Race conditions when multiple workspaces emit results simultaneously
- Vim client code needs significant changes to manage multiple connections
- Scales poorly — every new workspace requires Vim to add a connection

### C. All instances forward everything through nginx to a single backend

Use nginx to multiplex all Socket.IO connections to one backend that handles Vim.

Rejected because:
- Conflates browser routing (workspace-specific) with Vim routing (workspace-agnostic)
- nginx Socket.IO routing is fragile with multiple backends on different paths
- Adds nginx configuration complexity for a problem solvable in application code

## Consequences

### Positive
- Multi-instance Vim reverse search works with zero Vim-side changes
- No new processes — master/worker is a mode of the existing pdf_server
- Backward compatible — single-instance deploys remain unchanged (is_master defaults to True)
- Hub logic (VimClient management) only runs in one process — no wasted resources
- Clean separation: worker instances are stateless relay points for Vim-bound messages

### Negative
- Master instance is a single point of failure for Vim connectivity (but not for browser — browsers remain independent)
- Slight latency increase for non-master reverse search: worker → HTTP POST → master → Socket.IO → Vim (one extra network hop on localhost, negligible)
- `create_app()` gains an `is_master` parameter — mild increase in conditional logic

### Risks
- If master instance is down, worker instances' HTTP POST to master will fail silently. Mitigation: log the failure on worker side; Vim user will notice reverse search stopped working and can check master status. Browser-side editor bridge path remains unaffected.

## Affected Scope

| File | Change |
|------|--------|
| `config.ini` | Add `[server] master = <workspace_name>` |
| `pdf_server.py` | `create_app(is_master)`: conditional Hub activation; new `/hub/reverse_search_result` endpoint on master; HTTP POST forwarding on worker |
| `pdf_server.py` `__main__` | Resolve `is_master` from config |

## Related

- ADR-0001: Parameterize static directory for multi-instance deployment
- `docs/issues/2026-04-04-140000/multi-instance-vim-dispatch.md`
