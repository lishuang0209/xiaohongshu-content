"""Build a source archive using an explicit file allowlist, never local data."""
import hashlib
import shutil
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = (
    'README.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md', '.gitignore',
    '.github/workflows/pages.yml',
    '小红书创作技能/SKILL.md', '小红书创作技能/agents/openai.yaml',
    '小红书创作技能/scripts/ensure_3x4.py',
    'docs/搜索工具安装与维护.md',
    'scripts/install_skill.py', 'scripts/ensure_3x4.py', 'scripts/prepare_xhs_browser.py',
    'scripts/setup_xhs_search.py', 'scripts/xhs_mcp_check.py',
    'scripts/build_release.py',
    '展示页/README.md', '展示页/dist/index.html',
    '展示页/dist/styles.css', '展示页/dist/app.js', '展示页/dist/room.svg',
)


def main():
    for relative in PUBLIC_FILES:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise SystemExit('Missing or symlinked source: ' + relative)
        path.resolve().relative_to(ROOT)
    target = ROOT / 'dist/xiaohongshu-content-source.zip'
    target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for relative in PUBLIC_FILES:
            archive.write(ROOT / relative, 'xiaohongshu-content/' + relative)
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise SystemExit('Archive validation failed.')
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(digest + '  ' + target.name + '\n')
    downloads = ROOT / '展示页/dist/downloads'
    downloads.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, downloads / target.name)
    shutil.copy2(ROOT / 'docs/搜索工具安装与维护.md', downloads / 'mcp-guide.md')
    shutil.copy2(ROOT / 'LICENSE', downloads / 'LICENSE')
    print(f'Created {target} ({len(PUBLIC_FILES)} files)')


if __name__ == '__main__':
    main()
