#!/usr/bin/env python3
"""news-image-20261125 entry: copy the pre-rendered image to the output dir.

Standard library only, no network. Deterministic: the same bytes every run.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # copyfile preserves content exactly; size check guards a truncated build.
    assert os.path.getsize(dst) == os.path.getsize(src)


if __name__ == "__main__":
    main()
