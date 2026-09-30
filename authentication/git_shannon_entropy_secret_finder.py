from pathlib import Path
import threading
import collections

frequency = collections.defaultdict(int)
threads = []
accumulator = 0

def get_files(repo_dir=Path.cwd()):

    repo_dir = Path(repo_dir).resolve()
    git_dir = repo_dir / ".git"

    for path in repo_dir.rglob("*"):
        if git_dir in path.parents or path == git_dir or "myenv" in path.parts or "myvenv" in path.parts or "build" in path.parts:
            continue
        if path.is_file():
            filename = str(path.resolve())
            t = threading.Thread(target=frequency_counter, args=(filename, accumulator,))
            t.start()
            threads.append(t)
        elif path.is_dir():
            print(f"Directory: {path}")

    for t in threads:
        t.join()

    print(frequency)


def frequency_counter(file, accumulator):
    with open(file, "r", encoding='utf-8', errors='ignore') as f:
        for line in f:
            for char in line:
                try:
                    char.encode('ascii', errors='strict')
                except UnicodeEncodeError:
                    continue
                accumulator += 1
                frequency[str(char)] += 1

get_files()

for key,value in frequency.items():
    frequency[key] = value/accumulator

print(frequency)