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


def create_app(static_dir=None):
    if static_dir is None:
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

    app = Flask(__name__, static_folder=static_dir, static_url_path='/static')
    CORS(app, origins="*")
    socketio.init_app(app, cors_allowed_origins="*")

    # === Forward search ===
    # compile_and_sync.sh calls curl /send_pdf_reload -> emit("pdf_control") -> browser jumps
    from send_socket_message_to_pdfjs import pdf_routes
    app.register_blueprint(pdf_routes)

    # === Vim client 连接管理 ===
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

    # === Reverse search ===
    # Browser double-click PDF -> emit("pdf_control_receive") -> forward to Vim via task
    @socketio.on('pdf_control_receive')
    def handle_reverse_search(data):
        # 转发给所有连接的 Vim 客户端（改用广播 reverse_search_result，由 channel.py 监听）
        # for sid, client in vim_clients.items():
        #     try:
        #         client.send_task("run_python_vim_script", "pdfsync_decode", data)
        #     except Exception as e:
        #         print(f"[pdf_server] Failed to forward to {sid}: {e}")

        # 同时本地也处理（返回给浏览器显示）
        try:
            from tools.pdfsync_decode import handler
            filepath, line = handler(**data)
            print(f"[pdf_server] reverse search: {filepath}:{line}", flush=True)
            socketio.emit('reverse_search_result', {
                'file': str(filepath),
                'line': int(line),
            })
        except Exception as e:
            socketio.emit('reverse_search_result', {
                'error': str(e),
            })

    # === Index: redirect to PDF viewer ===
    @app.route("/")
    def index():
        return redirect('/static/pdfjs/web/viewer_patched.html?file=static/main.pdf')

    # === Health check ===
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "server": "pdf_server"})

    return app


if __name__ == '__main__':
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    if not os.path.exists(config_path):
        print(f"[ERROR] config.ini not found at {config_path}\n"
              f"Please copy config.ini.example to config.ini and set your port.",
              file=sys.stderr)
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)
    port = config.getint('server', 'port')
    host = '0.0.0.0'

    if not check_port(host, port):
        print(f"[ERROR] Port {port} is already in use. "
              f"Another server (channel.py?) may be running.", file=sys.stderr)
        sys.exit(1)

    print(f"[pdf_server] Starting on http://{host}:{port}")
    app = create_app()
    socketio.run(app, host=host, port=port, allow_unsafe_werkzeug=True)
