#!/usr/bin/env python3
"""
pdf_server.py — Standalone PDF viewer server (ADR-0003)

Does not depend on Vim, channel.py, or worker.vim.
Provides PDF forward search (browser page jump) and reverse search (source file + line).

Usage:
    python pdf_server.py                          # default 0.0.0.0:7777
    python pdf_server.py --host 127.0.0.1 --port 8080
"""
import argparse
import configparser
import os
import socket
import sys

from flask import Flask, redirect, jsonify, request as flask_request
from flask_cors import CORS
from socketapp import socketio, state


# === Vim client 管理（复用 llmos/server2.py 模式） ===
class VimClient:
    def __init__(self, sid):
        self.sid = sid
        vim_clients[sid] = self
        print(f"[pdf_server] Vim client connected: {sid}")

    def send_task(self, command, target, args):
        msg = {"command": command, "target": target, "args": args}
        socketio.emit("task", msg, room=self.sid)
        print(f"[pdf_server] Task sent to {self.sid}: target={target}")

vim_clients = {}


def check_port(host, port):
    """Check if port is already in use (ignores TIME-WAIT)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def create_app(static_dir=None, is_master=True, master_url=None):
    """
    Create the Flask app.

    Args:
        static_dir: workspace directory for PDF/synctex/JSON files
        is_master: if True, run Hub (Vim dispatch) + Worker; if False, Worker only
        master_url: base URL of master instance (e.g. "http://127.0.0.1:7777"),
                    used by workers to forward reverse search results
    """
    if static_dir is None:
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

    app = Flask(__name__, static_folder=static_dir, static_url_path='/static')
    CORS(app, origins="*")
    socketio.init_app(app, cors_allowed_origins="*")

    # === Forward search ===
    # compile_and_sync.sh calls curl /send_pdf_reload -> emit("pdf_control") -> browser jumps
    from send_socket_message_to_pdfjs import pdf_routes
    app.register_blueprint(pdf_routes)

    # === Hub: Vim client management (master only) ===
    if is_master:
        @socketio.on('connect')
        def on_vim_connect():
            sid = str(flask_request.sid)
            VimClient(sid)

        @socketio.on('disconnect')
        def on_vim_disconnect():
            sid = str(flask_request.sid)
            removed = vim_clients.pop(sid, None)
            if removed:
                print(f"[pdf_server] Vim client disconnected: {sid}")

        @socketio.on('task_result')
        def on_task_result(data):
            pass  # 反向查找不需要返回值

        # === Reverse search result relay ===
        # When a client (e.g. math VitePress) already knows file+line,
        # it emits reverse_search_result directly. Relay to all other clients.
        @socketio.on('reverse_search_result')
        def relay_reverse_search(data):
            from flask_socketio import emit
            print(f"[pdf_server] relay reverse_search_result: {data}", flush=True)
            emit('reverse_search_result', data, broadcast=True)

        # === Hub endpoint: receive forwarded results from worker instances ===
        @app.route("/hub/reverse_search_result", methods=["POST"])
        def hub_receive_reverse_search():
            data = flask_request.get_json()
            print(f"[pdf_server:hub] received from worker: {data}", flush=True)
            socketio.emit('reverse_search_result', data)
            return jsonify({"status": "ok"})

    def _forward_to_master(result_data):
        """Worker: forward reverse search result to master via HTTP POST."""
        import requests
        url = f"{master_url}/hub/reverse_search_result"
        try:
            resp = requests.post(url, json=result_data, timeout=3)
            print(f"[pdf_server:worker] forwarded to master: {resp.status_code}", flush=True)
        except Exception as e:
            print(f"[pdf_server:worker] failed to forward to master: {e}", flush=True)

    # === Reverse search ===
    # Browser double-click PDF -> emit("pdf_control_receive") -> SyncTeX reverse lookup
    @socketio.on('pdf_control_receive')
    def handle_reverse_search(data):
        print(f"[pdf_server] reverse search request: {data}", flush=True)

        try:
            from synctex_tool import reverse_lookup
            import json

            json_dir = os.path.join(static_dir, '')
            with open(os.path.join(json_dir, 'reverse_map.json'), 'r') as f:
                reverse_map = json.load(f)
            with open(os.path.join(json_dir, 'file_map.json'), 'r') as f:
                file_map = json.load(f)

            result = reverse_lookup(
                reverse_map, file_map,
                page=data.get('pageNumber'),
                x=data.get('pageX_pdf'),
                y=data.get('pageY_pdf'),
            )
            print(f"[pdf_server] reverse search: {result['file']}:{result['line']}", flush=True)
            result_data = {'file': result['file'], 'line': result['line']}

            # Local broadcast (for browser editor bridge)
            socketio.emit('reverse_search_result', result_data)

            # Worker: also forward to master for Vim dispatch
            if not is_master and master_url:
                _forward_to_master(result_data)

        except Exception as e:
            print(f"[pdf_server] reverse search error: {e}", flush=True)
            socketio.emit('reverse_search_result', {'error': str(e)})

    # === Index: redirect to PDF viewer ===
    @app.route("/")
    def index():
        return redirect('/static/pdfjs/web/viewer_patched.html?file=static/main.pdf')

    # === Health check ===
    @app.route("/health")
    def health():
        return jsonify({
            "status": "ok",
            "server": "pdf_server",
            "role": "master" if is_master else "worker",
        })

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PDF preview server with SyncTeX support')
    parser.add_argument('--static-dir', default=None,
                        help='Path to static directory (default: <script_dir>/static)')
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=None,
                        help='Port (default: resolved from config.ini [workspaces])')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.ini')
    if not os.path.exists(config_path):
        print(f"[ERROR] config.ini not found at {config_path}\n"
              f"Please copy config.ini.example to config.ini and set your port.",
              file=sys.stderr)
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)

    # Resolve static_dir
    static_dir = args.static_dir
    if static_dir is None:
        static_dir = os.path.join(script_dir, 'static')
    static_dir = os.path.abspath(static_dir)
    dir_name = os.path.basename(static_dir)

    # Resolve port: CLI flag > [workspaces] > [server]
    host = args.host
    if args.port is not None:
        port = args.port
    elif config.has_section('workspaces') and config.has_option('workspaces', dir_name):
        port = config.getint('workspaces', dir_name)
    else:
        port = config.getint('server', 'port')

    if not check_port(host, port):
        print(f"[ERROR] Port {port} is already in use. "
              f"Another server (channel.py?) may be running.", file=sys.stderr)
        sys.exit(1)

    # Resolve master/worker role
    master_name = config.get('server', 'master', fallback=None)
    is_master = (master_name is None) or (dir_name == master_name)
    master_url = None
    if not is_master and master_name:
        if config.has_option('workspaces', master_name):
            master_port = config.getint('workspaces', master_name)
            master_url = f"http://127.0.0.1:{master_port}"

    role = "master" if is_master else "worker"
    print(f"[pdf_server] Starting on http://{host}:{port}  static_dir={static_dir}  role={role}")
    if master_url:
        print(f"[pdf_server] Master at {master_url}")
    app = create_app(static_dir=static_dir, is_master=is_master, master_url=master_url)
    socketio.run(app, host=host, port=port, allow_unsafe_werkzeug=True)
