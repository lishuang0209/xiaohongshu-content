import argparse, base64, json, os, tomllib, urllib.request
from pathlib import Path

parser = argparse.ArgumentParser(description='只读检查本地 MCP，或获取登录二维码。Python 3.11+。')
parser.add_argument('mode', choices=['list','check_login_status','get_login_qrcode','search_feeds','get_feed_detail'])
parser.add_argument('arguments', nargs='?', default='{}', help='工具参数 JSON')
args = parser.parse_args()
codex_dir = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))).expanduser()
config = tomllib.loads((codex_dir / 'config.toml').read_text())['mcp_servers']['xiaohongshu_search']
if config['url'] != 'http://127.0.0.1:18060/mcp':
    raise SystemExit('This helper only sends credentials to the configured local endpoint.')
headers = {'Content-Type':'application/json', 'Accept':'application/json, text/event-stream', **config['http_headers']}

def call(method, params):
    data = json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode()
    req = urllib.request.Request(config['url'], data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as response:
        result = json.load(response)
    if 'error' in result:
        raise RuntimeError(result['error'])
    return result['result']

mode = args.mode
if mode == 'list':
    init = call('initialize', {'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'local-setup-check','version':'1'}})
    print('MCP connected:', init.get('serverInfo'))
    result = call('tools/list', {})
    selected = [t for t in result['tools'] if t['name'] in config['enabled_tools']]
    assert len(selected) == len(config['enabled_tools'])
    print(json.dumps(selected, ensure_ascii=False))
else:
    assert mode in config['enabled_tools']
    tool_args = json.loads(args.arguments)
    result = call('tools/call', {'name':mode,'arguments':tool_args})
    for item in result.get('content', []):
        if item.get('type') == 'image':
            path = codex_dir / 'tools/xiaohongshu-mcp/session/login-qr.png'
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            path.write_bytes(base64.b64decode(item['data']))
            path.chmod(0o600)
            print('QR_IMAGE_PATH:', path)
        elif item.get('type') == 'text':
            print(item['text'])
    if result.get('isError'):
        raise SystemExit(2)
