from pathlib import Path
import re

"""
Package structure (package.spm)

| readme.md
| meta.msgpack
| license
|_ tests/
|_ src/
    |_ my_package/
        |_ __init__.py
        |_ script.py
        |_ ....
        
"""

def validate(directory):
    missing = []

    expected_dirs = ["tests", "src"]
    expected_files = ["readme.md", "meta.msgpack", "license"]

    path = Path(directory)

    for d in expected_dirs:
        print(path / d)
        if not (path / d).is_dir():
            missing.append(d)

    for f in expected_files:
        print(path / f)
        if not (path/ f).is_file():
            missing.append(f)

    src_dir = path / "src"
    if src_dir.is_dir():
        init_files = list(src_dir.glob("*/__init__.py"))
        if not init_files:
            missing.append("src/<package_name>/__init__.py")
        else:
            package_name = init_files[0].parent

    if missing:
        return missing
    else:
        return package_name

file_match = re.compile(r"$[^\.]+\.py^")

def security_check(src_path):
    src_path = Path(src_path)
    files = [f for f in src_path.glob("*")]
    for f in files:
        if f.is_dir():
            return {0: "src contains nested directories"}
        if not re.match(file_match, str(f)):
            return {0: f"src contains non-python file, or file with invalid character (.): {f}"}

        base = Path(src_path).resolve()

        target = base.joinpath(f).resolve()
        try: 
            target.relative_to(base)
        except ValueError:
            return {0: f"Path traversal characters detected within source file name {f}"}


    return {1: None}


    