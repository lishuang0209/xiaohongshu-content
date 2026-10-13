"""Copy the visible skill source into Codex and Cursor skill directories."""
import argparse
import filecmp
import shutil
from pathlib import Path

SKILL_NAME = 'xiaohongshu-content'
PROJECT_RELATIVE = (
    Path('.agents/skills') / SKILL_NAME,
    Path('.cursor/skills') / SKILL_NAME,
)
USER_RELATIVE = Path('.cursor/skills') / SKILL_NAME
IGNORE_NAMES = ['__pycache__', '.DS_Store']


def trees_match(left, right):
    comparison = filecmp.dircmp(left, right, ignore=IGNORE_NAMES)
    if comparison.left_only or comparison.right_only or comparison.funny_files or comparison.common_funny:
        return False
    for name in comparison.diff_files:
        if not filecmp.cmp(left / name, right / name, shallow=False):
            return False
    return all(trees_match(left / name, right / name) for name in comparison.subdirs)


def install_state(source, target):
    """Return 'missing', 'same', or 'different'."""
    if target.is_symlink():
        try:
            return 'same' if target.resolve() == source.resolve() else 'different'
        except OSError:
            return 'different'
    if not target.exists():
        return 'missing'
    if target.is_dir() and trees_match(source, target):
        return 'same'
    return 'different'


def main():
    parser = argparse.ArgumentParser(
        description='将技能安装到项目的 Codex 与 Cursor 技能目录；内容不同的已有安装不会覆盖。'
    )
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument(
        '--user',
        action='store_true',
        help='同时安装到用户目录 ~/.cursor/skills/xiaohongshu-content',
    )
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / '小红书创作技能'
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        parser.error('目标项目文件夹不存在。')
    if not source.is_dir():
        parser.error('技能源目录不存在。')

    targets = [project / relative for relative in PROJECT_RELATIVE]
    if args.user:
        targets.append(Path.home() / USER_RELATIVE)

    states = [(target, install_state(source, target)) for target in targets]
    conflicts = [target for target, state in states if state == 'different']
    if conflicts:
        listed = '\n'.join('  ' + str(target) for target in conflicts)
        parser.error('目标已存在且与当前技能不同，本脚本不覆盖：\n' + listed)

    for target, state in states:
        if state == 'same':
            print('Already installed:', target)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, ignore=shutil.ignore_patterns(*IGNORE_NAMES))
        print('Installed:', target)


if __name__ == '__main__':
    main()
