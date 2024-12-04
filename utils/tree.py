from pathlib import Path

def print_tree(dir_path: Path, prefix: str = ''):
    # Get all entries, excluding hidden files
    entries = sorted([x for x in dir_path.iterdir() if not x.name.startswith('.')])
    
    # Sort directories first, then files
    entries = sorted(entries, key=lambda x: (not x.is_dir(), x.name.lower()))
    
    # Print each entry
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        print(f'{prefix}{"└── " if is_last else "├── "}{entry.name}')
        if entry.is_dir():
            print_tree(entry, prefix + ('    ' if is_last else '│   '))

if __name__ == '__main__':
    print_tree(Path('.'))