import os

def listdir_depth(path, depth=2, prefix=""):
    if depth < 0:
        return
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        print(f"{prefix}[Нет доступа]")
        return

    for i, item in enumerate(items):
        path_item = os.path.join(path, item)
        is_last = i == len(items) - 1
        branch = "└── " if is_last else "├── "
        print(f"{prefix}{branch}{item} {'/' if os.path.isdir(path_item) else ''}")

        if os.path.isdir(path_item):
            new_prefix = prefix + ("    " if is_last else "│   ")
            listdir_depth(path_item, depth - 1, new_prefix)

if __name__ == "__main__":
    listdir_depth(".", depth=2)
