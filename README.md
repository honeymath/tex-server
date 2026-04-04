# tex-server

LaTeX PDF preview server with SyncTeX bidirectional search.

Compile LaTeX, view PDF in browser, click source to jump to PDF (forward search), double-click PDF to jump back to source (reverse search).

## Architecture

```
compile_and_sync.sh          pdf_server.py              Browser
 (compile LaTeX)         (Flask + Socket.IO)        (PDF.js viewer)
        |                        |                        |
        | copy PDF/synctex       |   /static/main.pdf     |
        |-----> [workspace dir]  |<-----------------------|
        |                        |                        |
        | curl /send_pdf_reload  |  emit("pdf_control")   |
        |----------------------->|----------------------->|  forward search
        |                        |                        |
        |                        | emit("pdf_control_receive")
        |                        |<-----------------------|  reverse search
        |                        | read reverse_map.json  |
        |                        | emit("reverse_search_result")
        |                        |----------------------->|
```

## Quick Start

### 1. Install dependencies

```bash
pip install flask flask-cors flask-socketio
```

`pdflatex` and `synctex` must be available on `$PATH` (included in TeX Live / MiKTeX).

### 2. Set up PDF.js

Run the setup script with a PDF.js version number:

```bash
./setup_pdfjs.sh 5.3.31
```

This will:
1. Download the PDF.js legacy dist from GitHub releases
2. Extract to `../pdf.js`
3. Run `generate_injected_pdfjs_viewer.py` to patch `viewer.html` → `viewer_patched.html` (injects Socket.IO, reverse search scripts, mobile meta tags, custom CSS)
4. Create symlink `static/pdfjs` → `../../pdf.js`

To update PDF.js later, run the same command with a new version number.

### 3. Configure

```bash
cp config.ini.example config.ini
```

Edit `config.ini` to set your port:

```ini
[server]
port = 7777

[workspaces]
static = 7777
```

### 4. Start the server

```bash
python pdf_server.py
```

Open browser: `http://localhost:7777`

### 5. Compile and forward search

```bash
./compile_and_sync.sh /path/to/chapter.tex 42
```

This compiles LaTeX, copies the PDF to the workspace directory, and tells the browser to jump to the corresponding location.

## Parameters

### pdf_server.py

```
python pdf_server.py [--static-dir DIR] [--host HOST] [--port PORT]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--static-dir` | `<script_dir>/static` | Workspace directory containing PDF and synctex files |
| `--host` | `0.0.0.0` | Bind address |
| `--port` | from `config.ini` | Server port. Resolution order: CLI flag > `[workspaces]` > `[server]` |

### compile_and_sync.sh

```
./compile_and_sync.sh <searchfile> <line> [zoom] [refresh] [output_dir]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `searchfile` | yes | | Path to the `.tex` file being edited |
| `line` | yes | | Cursor line number |
| `zoom` | no | `1.0` | Zoom level |
| `refresh` | no | `1` | Whether to reload the page |
| `output_dir` | no | `<script_dir>/static` | Workspace directory for output |

The script finds `main.tex` by searching upward from the given file. Port is resolved from `config.ini [workspaces]` by directory name.

## Multi-Workspace Deployment

Run multiple independent server instances, each with its own workspace directory and port. Workspaces are fully isolated at the OS process level.

### 1. Define workspaces in config.ini

```ini
[workspaces]
static  = 7777
alpha   = 7771
beta    = 7772
gamma   = 7773
delta   = 7774
epsilon = 7775
```

### 2. Create workspace directories

Each workspace directory needs symlinks to shared assets:

```bash
mkdir -p alpha
ln -s static/pdfjs alpha/pdfjs
ln -s static/tex-server alpha/tex-server
```

Repeat for each workspace. Only `pdfjs/` and `tex-server/` are shared. PDF, synctex, and JSON map files are per-workspace.

### 3. Start each instance

```bash
python pdf_server.py --static-dir ./alpha
python pdf_server.py --static-dir ./beta
```

Each instance auto-resolves its port from `config.ini [workspaces]` by directory name.

### 4. Compile to a specific workspace

```bash
./compile_and_sync.sh /path/to/chapter.tex 42 1.0 1 ./alpha
```

## Nginx Reverse Proxy

To serve all workspaces behind a single nginx host, use path-prefix routing.

### nginx config

Add a `map` block in the `http` context to mirror `config.ini [workspaces]`:

```nginx
map $tex_workspace $tex_port {
    static   7777;
    alpha    7771;
    beta     7772;
    gamma    7773;
    delta    7774;
    epsilon  7775;
    default  7777;
}
```

Add a single location block in your `server` context:

```nginx
# /w/<workspace>/... -> localhost:<port>/...
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

### Access via browser

```
https://your-host/w/alpha/     -> workspace alpha
https://your-host/w/beta/      -> workspace beta
https://your-host/w/static/    -> default workspace
```

The frontend auto-detects the path prefix from the URL. Socket.IO connections and API requests are routed to the correct backend automatically.

## Editor Integration (Reverse Search)

When you double-click the PDF in the browser, the server performs a reverse search and emits the source file and line number. To open the result in your editor:

1. Copy `user_config.example.js` to `user_config.js`:

```bash
cp static/tex-server/user_config.example.js static/tex-server/user_config.js
```

2. Edit `user_config.js`:

```javascript
export const EDITOR_BRIDGE_ENABLED = true;
export const EDITOR_BRIDGE_URL = "http://localhost:7777";
```

The browser sends a request to `EDITOR_BRIDGE_URL/open?filename=...&line=...` on each reverse search result. Configure your editor to listen on that endpoint.

## File Structure

```
tex-server/
  pdf_server.py              # Main server (Flask + Socket.IO)
  compile_and_sync.sh        # LaTeX compile + forward search
  synctex_tool.py            # SyncTeX parser (CLI, no external deps)
  socketapp.py               # Shared Socket.IO instance
  send_socket_message_to_pdfjs.py  # Forward search HTTP->Socket.IO bridge
  setup_pdfjs.sh             # Download and patch PDF.js
  generate_injected_pdfjs_viewer.py  # Patch viewer.html with Socket.IO scripts
  config.ini                 # Port config (gitignored)
  config.ini.example         # Template for config.ini
  static/                    # Default workspace
    pdfjs/                   #   PDF.js viewer (symlink)
    tex-server/              #   Frontend JS
      config.js              #     Socket.IO + path prefix config
      sync_socket_io.js      #     Forward search handler
      double_click_page_position.js  # Reverse search click handler
      user_config.js         #     Editor bridge config (gitignored)
    main.pdf                 #   Compiled PDF (gitignored)
    *.json                   #   SyncTeX lookup maps (gitignored)
  alpha/, beta/, ...         # Additional workspaces (gitignored)
```
