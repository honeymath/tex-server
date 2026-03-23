# inject_socket.py

INPUT_FILE = '../pdf.js/web/viewer.html'
OUTPUT_FILE = '../pdf.js/web/viewer_patched.html'

# Injection lines to be added before the closing </body> tag
INJECTION_LINES = [
'<script type="module" src="../../tex-server/double_click_page_position.js"></script>',
'<script src="https://cdn.socket.io/4.6.0/socket.io.min.js"></script>',
'<script type="module" src="../../tex-server/sync_socket_io.js"></script>'
]

HEADER_LINES = [
'<meta name="apple-mobile-web-app-capable" content="yes">',
'<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'
]


HEADER_ENDLINES = [
'<link rel="stylesheet" href="../../tex-server/viewer_patched.css">'
]

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 插入到 </body> 前
    injection_block = '\n'.join(INJECTION_LINES) + '\n'
    if '</body>' in content:
        content = content.replace('</body>', f'{injection_block}</body>')
        print('[inject_socket.py] Injection applied.')
    else:
        print('[inject_socket.py] ERROR: </body> tag not found!')
        return

    header_block = '\n'.join(HEADER_LINES) + '\n'
    # 插入到 <head> 中
    if '<head>' in content:
        content = content.replace('<head>', f'<head>\n{header_block}')
        print('[inject_socket.py] Header lines injected.')
    else:
        print('[inject_socket.py] ERROR: <head> tag not found!')

    # 插入到 </head> 前
    if '</head>' in content:
        endline_block = '\n'.join(HEADER_ENDLINES) + '\n'
        content = content.replace('</head>', f'{endline_block}</head>')
        print('[inject_socket.py] Header end lines injected.')


    # 写到 output 文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'[inject_socket.py] Output written to {OUTPUT_FILE}')

if __name__ == '__main__':
    main()

