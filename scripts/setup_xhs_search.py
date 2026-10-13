import argparse
import platform
import hashlib
import os
import plistlib
import secrets
import shutil
import subprocess
import time
import tomllib
from pathlib import Path

parser = argparse.ArgumentParser(description='在 Apple Silicon Mac 安装本地小红书搜索 MCP（Python 3.11+）。')
parser.add_argument('--binary', type=Path, default=Path(__file__).resolve().parents[1] / '本地资料/安装包/xiaohongshu-mcp-darwin-arm64')
args = parser.parse_args()
if platform.system() != 'Darwin' or platform.machine() != 'arm64':
    raise SystemExit('This installer supports Apple Silicon macOS only.')
source = args.binary
browser = Path.home() / 'Library/Caches/xiaohongshu-mcp/browser/148.0.7778.215/Chromium.app/Contents/MacOS/Chromium'
if not browser.is_file():
    raise SystemExit('Prepare the browser first: python3 scripts/prepare_xhs_browser.py')
expected = 'fad3633fda4a8060e66e2941bc8fc5460326c7cb4e58a32485a9e2c9408e95a8'
if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
    raise SystemExit('Release checksum mismatch; installation stopped.')

codex_dir = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))).expanduser()
base = codex_dir / 'tools/xiaohongshu-mcp'
config = codex_dir / 'config.toml'
original = config.read_text() if config.exists() else ''
parsed = tomllib.loads(original)
if 'xiaohongshu_search' in parsed.get('mcp_servers', {}):
    raise SystemExit('An existing xiaohongshu_search configuration needs review.')
agent = Path.home() / 'Library/LaunchAgents/com.codex.xiaohongshu-search.plist'
if agent.exists():
    raise SystemExit('An existing launch agent needs review.')

os.umask(0o077)
base.mkdir(parents=True, exist_ok=True)
base.chmod(0o700)
(base / 'session').mkdir(exist_ok=True)
(base / 'session').chmod(0o700)
binary = base / 'xiaohongshu-mcp'
shutil.copyfile(source, binary)
binary.chmod(0o700)
token = secrets.token_urlsafe(32)
block = '\n\n[mcp_servers.xiaohongshu_search]\n'
block += 'url = "http://127.0.0.1:18060/mcp"\n'
block += 'enabled = true\n'
block += 'enabled_tools = ["check_login_status", "get_login_qrcode", "search_feeds", "get_feed_detail"]\n'
block += 'startup_timeout_sec = 20\n'
block += 'tool_timeout_sec = 120\n'
block += 'http_headers = { Authorization = "Bearer ' + token + '" }\n'
updated = original.rstrip() + block
tomllib.loads(updated)
backup = config.with_name('config.toml.before-xhs-' + str(int(time.time())))
if config.exists():
    shutil.copy2(config, backup)
    backup.chmod(0o600)
temp = config.with_name('config.toml.xhs-installing')
temp.write_text(updated)
temp.chmod(0o600)

spec = {
    'Label': 'com.codex.xiaohongshu-search',
    'ProgramArguments': [str(binary), '-headless=true', '-port', '127.0.0.1:18060'],
    'WorkingDirectory': str(base),
    'EnvironmentVariables': {'AUTH_TOKEN': token, 'COOKIES_PATH': str(base / 'session/cookies.json')},
    'RunAtLoad': True,
    'KeepAlive': True,
    'ThrottleInterval': 30,
    'StandardOutPath': str(base / 'service.out.log'),
    'StandardErrorPath': str(base / 'service.err.log'),
}
agent.parent.mkdir(parents=True, exist_ok=True)
agent.write_bytes(plistlib.dumps(spec))
agent.chmod(0o600)
os.replace(temp, config)
result = subprocess.run(['launchctl', 'bootstrap', 'gui/' + str(os.getuid()), str(agent)], capture_output=True, text=True)
if result.returncode:
    config.write_text(original)
    config.chmod(0o600)
    agent.unlink()
    raise SystemExit('Service registration failed; configuration restored: ' + result.stderr)
print('Official v2.5.5 checksum verified. Local service registered; four login/read tools configured.')
