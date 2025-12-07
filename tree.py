#!/usr/bin/env python3
import argparse
from pathlib import Path

def print_tree(directory: Path, prefix: str = '', is_last: bool = True, max_depth: int = None, current_depth: int = 0, show_dirs_only: bool = False):
    if max_depth is not None and current_depth > max_depth:
        return

    connector = '└── ' if is_last else '├── '
    print(prefix + connector + directory.name)

    if directory.is_file():
        return

    # Определяем новый префикс для вложенных элементов
    if is_last:
        extension = '    '
    else:
        extension = '│   '

    new_prefix = prefix + extension

    try:
        children = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name))
    except PermissionError:
        return  # Пропускаем директории, к которым нет доступа

    entries = [child for child in children if not child.name.startswith('.')]  # Игнорируем скрытые файлы

    for i, child in enumerate(entries):
        is_last_child = (i == len(entries) - 1)
        if child.is_dir():
            print_tree(child, new_prefix, is_last_child, max_depth, current_depth + 1, show_dirs_only)
        elif not show_dirs_only:
            print(new_prefix + ('└── ' if is_last_child else '├── ') + child.name)

def main():
    parser = argparse.ArgumentParser(description='Показывает структуру директории в виде дерева.')
    parser.add_argument('directory', nargs='?', default='.', help='Директория для отображения (по умолчанию — текущая)')
    parser.add_argument('-d', action='store_true', help='Показывать только директории')
    parser.add_argument('-L', type=int, help='Максимальная глубина вложенности')

    args = parser.parse_args()

    path = Path(args.directory)
    if not path.exists():
        print(f"Ошибка: путь '{path}' не существует.")
        return

    print(path.name + '/')
    print_tree(path, show_dirs_only=args.d, max_depth=args.L)

    # Подсчёт файлов и директорий
    def count_items(p: Path, max_depth=None, current_depth=0, show_dirs_only=False):
        if max_depth is not None and current_depth > max_depth:
            return 0, 0
        dirs, files = 0, 0
        try:
            for item in p.iterdir():
                if item.name.startswith('.'):
                    continue
                if item.is_dir():
                    d, f = count_items(item, max_depth, current_depth + 1, show_dirs_only)
                    dirs += 1 + d
                    files += f
                elif not show_dirs_only:
                    files += 1
        except PermissionError:
            pass
        return dirs, files

    total_dirs, total_files = count_items(path, args.L)
    print(f"\n{total_dirs} директорий, {total_files} файлов")

if __name__ == '__main__':
    main()
