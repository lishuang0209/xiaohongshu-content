from pathlib import Path
import argparse, hashlib, platform, subprocess, tempfile

parser = argparse.ArgumentParser(description='核验并安装 MCP 所需浏览器，不移除 macOS 安全属性。')
parser.add_argument('--archive', type=Path, default=Path(__file__).resolve().parents[1] / '本地资料/安装包/macos-arm64.dmg')
args = parser.parse_args()
if platform.system() != 'Darwin' or platform.machine() != 'arm64':
    raise SystemExit('This installer supports Apple Silicon macOS only.')
archive = args.archive
expected = 'b72f091e2e1a7583eed389c4b8e3534ed355e568af8c8bbf8fc30a25e23ca679'
if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
    raise SystemExit('Browser checksum mismatch; stopped.')
target = Path.home() / 'Library/Caches/xiaohongshu-mcp/browser/148.0.7778.215'
target.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='xhs-browser-') as mount:
    subprocess.run(['hdiutil', 'attach', str(archive), '-readonly', '-nobrowse', '-mountpoint', mount], check=True, capture_output=True)
    try:
        apps = list(Path(mount).glob('*.app'))
        assert len(apps) == 1, 'Expected one browser application'
        dst = target / apps[0].name
        assert not dst.exists(), 'Browser already exists; inspect before replacing'
        subprocess.run(['ditto', str(apps[0]), str(dst)], check=True)
        assert (dst / 'Contents/MacOS/Chromium').is_file()
        print('Browser checksum verified and component installed:', dst)
    finally:
        subprocess.run(['hdiutil', 'detach', mount, '-quiet'], check=True)
