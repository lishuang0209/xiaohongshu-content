"""Copy the visible skill source into a project's skill discovery directory."""
import argparse
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='将技能安装到项目，不覆盖已有技能。')
    parser.add_argument('--project', type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / '小红书创作技能'
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        parser.error('目标项目文件夹不存在。')
    target = project / '.agents/skills/xiaohongshu-content'
    if target.is_symlink() or target.exists():
        if target.resolve() == source:
            print('该项目已连接当前技能。')
            return
        parser.error('目标已存在，请自行备份或比较后处理；本脚本不覆盖。')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '.DS_Store'))
    print('Installed:', target)


if __name__ == '__main__':
    main()
