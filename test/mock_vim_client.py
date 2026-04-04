#!/usr/bin/env python3
"""
mock_vim_client.py — Simulates Vim's channel.py for testing.

Connects to the master pdf_server via Socket.IO and listens for
reverse_search_result events, printing them to stdout.

Usage:
    python test/mock_vim_client.py [master_url]
    python test/mock_vim_client.py http://127.0.0.1:7777

The script exits after receiving one event (or after timeout).
"""
import sys
import socketio
import time

master_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:7777"
received = []

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print(f"[mock_vim] connected to {master_url}", flush=True)

@sio.on('reverse_search_result')
def on_reverse_search(data):
    print(f"[mock_vim] GOT reverse_search_result: {data}", flush=True)
    received.append(data)

@sio.on('disconnect')
def on_disconnect():
    print("[mock_vim] disconnected", flush=True)

print(f"[mock_vim] connecting to {master_url}...", flush=True)
sio.connect(master_url, transports=['websocket'])

# Wait up to 30 seconds for a result
deadline = time.time() + 30
while time.time() < deadline and not received:
    time.sleep(0.5)

if received:
    print(f"[mock_vim] SUCCESS — received {len(received)} result(s)", flush=True)
else:
    print("[mock_vim] TIMEOUT — no result received", flush=True)

sio.disconnect()
sys.exit(0 if received else 1)
