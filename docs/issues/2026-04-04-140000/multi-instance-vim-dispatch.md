# Issue: Multi-Instance Deployment Breaks Vim Reverse Search Dispatch

## Summary

ADR-0001 introduces multi-instance deployment (one pdf_server process per workspace, each on a separate port). The PDF viewer browser side works correctly — nginx path-prefix routing ensures each browser connects to the right backend. However, the **Vim editor client** side has no working path to receive reverse search results in the multi-instance topology.

## Severity

**High** — Reverse search (PDF → editor) is a core feature. Multi-instance deployment is non-functional for Vim users until this is resolved.

## Current Architecture (Single Instance)

```
                  :7777
Vim ──socket.io──> pdf_server <──socket.io── Browser
       (channel.py)     │                  (PDF viewer)
                        │
            reverse_search_result
                        │
                   broadcast to
                   all clients
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
        Vim receives         Browser receives
        (opens file)         (editor bridge HTTP call)
```

**Flow:**
1. User double-clicks PDF in browser
2. Browser emits `pdf_control_receive` with `{pageNumber, pageX_pdf, pageY_pdf}`
3. `pdf_server.py:90-126` performs SyncTeX reverse lookup using `static_dir/reverse_map.json`
4. Server broadcasts `reverse_search_result` with `{file, line}` to ALL connected Socket.IO clients
5. **Vim path:** `vimconfig/channel.py:223-230` receives event, prints `COMe +{line} {file}` to stdout, `worker.vim:46-49` executes as Vim command
6. **Browser path:** `sync_socket_io.js:156-164` receives event, calls `EDITOR_BRIDGE_URL/open?filename=...&line=...`

This works because there is only one server — everyone connects to the same place.

## What Breaks with Multi-Instance

### Problem 1: Vim doesn't know which instance to connect to

`channel.py` connects to a single host:port. With workspaces on :7771, :7772, :7773 etc., Vim would need to connect to all of them simultaneously to receive reverse search results from any workspace.

### Problem 2: Vim is remote — no direct port access

Vim connects through nginx, which exposes a single host. The backend ports (7771-7775) are not directly accessible from Vim's network location. The current nginx workspace routing uses URL path prefixes (`/w/alpha/`, `/w/beta/`), but `channel.py`'s Socket.IO client connects to the **root** path — it has no concept of workspace path prefixes.

### Problem 3: Broadcast fan-out if Vim connects to multiple instances

Even if Vim could connect to all instances (e.g., by iterating over known workspace ports), simultaneous reverse search results from different workspaces would race:

```
alpha pdf_server → reverse_search_result {file: "alpha/ch1.tex", line: 42}
beta  pdf_server → reverse_search_result {file: "beta/ch3.tex", line: 10}
         ↓                    ↓
    both arrive at Vim simultaneously → which file does Vim open?
```

In practice this race is unlikely (user is only interacting with one PDF at a time), but architecturally it is unclean and will cause confusion in edge cases.

### Problem 4: Browser editor bridge has the same issue

`sync_socket_io.js:159` calls a hardcoded `EDITOR_BRIDGE_URL` from `user_config.js`. This URL is in the shared `tex-server/` directory (symlinked into all workspaces). All workspace browsers call the same editor bridge endpoint. This is less severe (each call carries the correct file+line), but the editor bridge itself may not distinguish workspace context.

## Affected Files

| File | Location | Role |
|------|----------|------|
| `pdf_server.py` | L82-86, L118-121 | Broadcasts `reverse_search_result` to all clients |
| `socketapp.py` | L3-4 | Per-process `SocketIO()` instance and `state` dict |
| `vimconfig/channel.py` | L223-230 | Receives `reverse_search_result`, dispatches to Vim |
| `vimconfig/channel.vim` | L72-78 | Opens Socket.IO connection to server |
| `static/tex-server/sync_socket_io.js` | L156-164 | Browser-side reverse_search_result handler |
| `static/tex-server/user_config.js` | L1-2 | Hardcoded `EDITOR_BRIDGE_URL` |

## Current Nginx Configuration

```nginx
# In http context: workspace-to-port mapping
map $tex_workspace $tex_port {
    static   7777;
    alpha    7771;
    beta     7772;
    gamma    7773;
    delta    7774;
    epsilon  7775;
    default  7777;
}

# In server context: workspace-aware routing
# Browser accesses /w/<workspace>/... → nginx strips prefix → backend receives /...
location ~ ^/w/(?P<tex_workspace>[^/]+)/(?P<tex_rest>.*)$ {
    proxy_pass http://127.0.0.1:$tex_port/$tex_rest$is_args$args;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_read_timeout 86400s;
    proxy_redirect / /w/$tex_workspace/;
}
```

This handles browser-to-backend routing. There is **no** equivalent route for Vim's Socket.IO connection.

## Proposed Topology: Central Hub (Dispatcher)

The correct architecture requires a **central hub** that acts as a message router:

```
  pdf_server:7771 (alpha)  ──┐
  pdf_server:7772 (beta)   ──┼──client──> Hub (:????) <──client── Vim (remote)
  pdf_server:7773 (gamma)  ──┘               ▲
                                             │
                                    nginx exposes hub
                                    on a single path
                                    (e.g. /hub/socket.io/)
```

**Key properties:**
- The hub is a **server**; pdf_server instances and Vim are both **clients** of the hub
- Each pdf_server instance connects to the hub on startup, identifying its workspace name
- Vim connects to the hub once (through nginx), not to individual pdf_server instances
- When a pdf_server emits `reverse_search_result`, the hub receives it and forwards to Vim
- When Vim sends a forward search command, the hub routes to the correct pdf_server based on workspace context
- The hub itself is stateless — pure message relay with workspace-tag routing

**Implications:**
- Vim no longer needs to know about individual workspace ports
- nginx only needs to expose one additional path for the hub's Socket.IO
- Hub can run as a lightweight standalone process (similar resource footprint to one pdf_server instance)
- Protocol change: messages must carry a `workspace` field so the hub can route

## Open Questions for Architect

1. **Hub placement:** New standalone process? Or extend an existing service?
2. **Protocol:** Should messages carry workspace ID, or should Socket.IO namespaces be used for routing?
3. **Hub discovery:** Should pdf_server instances register with the hub on startup, or should the hub read `config.ini [workspaces]` and connect to instances?
4. **Failure handling:** If the hub restarts, how do clients reconnect? If a pdf_server instance restarts, how does the hub notice?
5. **Browser path:** Should browsers also route through the hub (unified architecture), or keep direct nginx routing (current, simpler)?
6. **Backward compatibility:** Should single-instance deployments (no hub) still work as before?
