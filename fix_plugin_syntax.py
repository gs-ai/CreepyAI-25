#!/usr/bin/env python3
"""Fix common syntax issues in CreepyAI plugin modules."""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


TRIPLE_QUOTE_RE = re.compile(r'(?:"{3,}|\'{3,})')


class PluginSyntaxFixer:
    """Fixes common docstring and indentation mistakes in plugins."""

    def __init__(self, plugins_dir: Path, include: Sequence[str] | None = None, dry_run: bool = False, create_backup: bool = True):
        self.plugins_dir = plugins_dir
        self.include = set(include or [])
        self.dry_run = dry_run
        self.create_backup = create_backup

    def find_plugin_files(self) -> List[Path]:
        plugin_files: List[Path] = []
        for path in self.plugins_dir.rglob('*.py'):
            if path.name.startswith('__'):
                continue
            if self.include and path.stem not in self.include and path.name not in self.include:
                continue
            plugin_files.append(path)
        return plugin_files

    def fix_docstring_issues(self, content: str) -> str:
        content = TRIPLE_QUOTE_RE.sub(lambda m: m.group(0)[:3], content)

        lines = content.split('\n')
        open_quote: str | None = None
        for line in lines:
            stripped = line.strip()
            if stripped.count('"""') % 2 == 1:
                open_quote = '"""' if open_quote is None else None
            elif stripped.count("'''") % 2 == 1:
                open_quote = "'''" if open_quote is None else None

        if open_quote is not None:
            logger.debug("Detected unterminated docstring, appending closing %s", open_quote)
            lines.append(open_quote)

        return '\n'.join(lines)

    @staticmethod
    def fix_indentation_issues(content: str) -> str:
        content = content.replace('\t', '    ')
        lines = content.split('\n')
        current_block_indent = 0
        in_block = False

        for idx, line in enumerate(lines):
            if not line.strip():
                continue

            indent_level = len(line) - len(line.lstrip(' '))
            if re.match(r'\s*(class|def)\s+\w+', line):
                in_block = True
                current_block_indent = indent_level
                continue

            if in_block and indent_level <= current_block_indent:
                in_block = False

            if in_block and indent_level not in {current_block_indent, current_block_indent + 4}:
                lines[idx] = ' ' * (current_block_indent + 4) + line.lstrip()

        return '\n'.join(lines)

    def fix_file_syntax(self, file_path: Path) -> bool:
        try:
            original_content = file_path.read_text(encoding='utf-8')
        except Exception as exc:  # pragma: no cover - filesystem dependent
            logger.error("Failed to read %s: %s", file_path, exc)
            return False

        content = self.fix_docstring_issues(original_content)
        content = self.fix_indentation_issues(content)

        if content == original_content:
            logger.debug("No syntax issues found in %s", file_path.name)
            return False

        if self.dry_run:
            logger.info("[dry-run] Would update %s", file_path)
            return True

        try:
            if self.create_backup:
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                backup_path.write_text(original_content, encoding='utf-8')

            file_path.write_text(content, encoding='utf-8')
            logger.info("Fixed syntax issues in %s", file_path.name)
            return True
        except Exception as exc:  # pragma: no cover - filesystem dependent
            logger.error("Failed to write %s: %s", file_path, exc)
            return False

    def fix_all_plugins(self) -> Tuple[int, int]:
        plugin_files = self.find_plugin_files()
        fixed_files = 0
        for file_path in plugin_files:
            if self.fix_file_syntax(file_path):
                fixed_files += 1
        return len(plugin_files), fixed_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fix common syntax issues in CreepyAI plugins")
    parser.add_argument("--plugins-dir", type=Path, default=Path(__file__).resolve().parent / 'app' / 'plugins', help="Plugins directory")
    parser.add_argument("--include", nargs='*', help="Specific plugin module names or filenames to inspect")
    parser.add_argument("--dry-run", action='store_true', help="Preview changes without editing files")
    parser.add_argument("--no-backup", action='store_true', help="Do not create .bak backups")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    plugins_dir = args.plugins_dir.resolve()
    if not plugins_dir.exists():
        logger.error("Plugins directory does not exist: %s", plugins_dir)
        return 1

    fixer = PluginSyntaxFixer(
        plugins_dir=plugins_dir,
        include=args.include,
        dry_run=args.dry_run,
        create_backup=not args.no_backup,
    )
    total_files, fixed_files = fixer.fix_all_plugins()

    print(f"\nProcessed {total_files} plugin files, fixed {fixed_files} file{'s' if fixed_files != 1 else ''}.")
    if fixed_files > 0 and not args.no_backup and not args.dry_run:
        print("Backups of original files were created with '.bak' extension.")

    return 0


if __name__ == '__main__':  # pragma: no cover - CLI entry point
    sys.exit(main())
