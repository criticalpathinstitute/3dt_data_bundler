#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@c-path.org>
Date   : 2021-06-18
Purpose: Data bundler for 3DT data
"""

import argparse
import os
import re
import sys
from shutil import copy
from pathlib import Path
from typing import List, NamedTuple, Optional, TextIO


class Args(NamedTuple):
    """ Command-line arguments """
    in_dir: str
    out_dir: str
    manifest: TextIO
    skip_exts: List[str]


# --------------------------------------------------
def get_args() -> Args:
    """ Get command-line arguments """

    parser = argparse.ArgumentParser(
        description='Data bundler for 3DT data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i',
                        '--indir',
                        metavar='DIR',
                        help='Input directory',
                        required=True)

    parser.add_argument('-o',
                        '--outdir',
                        metavar='DIR',
                        help='Output directory',
                        required=True)

    parser.add_argument('-m',
                        '--manifest',
                        metavar='FILE',
                        type=argparse.FileType('wt'),
                        help='Manifest path',
                        default='manifest.txt')

    parser.add_argument('-s',
                        '--skip_exts',
                        metavar='STR',
                        help='Cxtensions for files to skip',
                        nargs='+',
                        default=['.wav', '.mp3', '.mp4', '.zip'])

    args = parser.parse_args()

    if not os.path.isdir(args.indir):
        parser.error(f'--indir "{args.indir}" is not a directory')

    out_dir = normalize(args.outdir)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    return Args(in_dir=args.indir,
                out_dir=out_dir,
                manifest=args.manifest,
                skip_exts=args.skip_exts)


# --------------------------------------------------
def main() -> None:
    """ Make a jazz noise here """

    args = get_args()
    in_dir = os.path.abspath(args.in_dir)
    files = filter(Path.is_file, Path(in_dir).rglob('*'))
    num_copied, num_total = 0, 0

    for i, path in enumerate(files, start=1):
        num_total += 1
        ext = os.path.splitext(path)[1]

        # Check for skip files
        if ext in args.skip_exts:
            print(f'{path} is skipped', file=sys.stderr)
            continue

        # Check for empty files
        if path.stat().st_size == 0:
            print(f'{path} is empty', file=sys.stderr)
            continue

        try:
            if empty := h5_is_empty(path):
                print(f'{path} is empty', file=sys.stderr)
                continue
        except Exception as e:
            print(f'{path} is corrupted ({e})', file=sys.stderr)
            continue

        relative_dir = normalize(
            re.sub('^[/]', '',
                   re.sub(in_dir, '', os.path.dirname(path.absolute()))))

        new_dir = os.path.join(args.out_dir, relative_dir)
        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)

        basename = normalize(os.path.basename(path))
        print(f'{i:5}: Copying {basename}')
        copy(path, os.path.join(new_dir, basename))
        print(os.path.join(relative_dir, basename), file=args.manifest)
        num_copied += 1

    print(f'Done, copied {num_copied:,} of {num_total:,} to "{args.out_dir}".')
    print(f'See manifest file "{args.manifest.name}".')


# --------------------------------------------------
def h5_is_empty(path: Path) -> bool:
    """ Test H5 file for emptiness/missing times """

    if path.suffix == '.h5':
        with h5py.File(path) as f:
            if sensors := f.get('Sensors'):
                times = list(
                    filter(None, map(lambda s: s.get('Time'),
                                     sensors.values())))

                return not times

            return True

    return False


# --------------------------------------------------
def normalize(s: Optional[str]) -> str:
    """ Normalize columns """

    if s:
        while True:
            match = re.search('(.*)([a-z])([A-Z].*)', s)
            if match:
                s = match.group(1) + match.group(2) + '_' + match.group(3)
            else:
                break

        s = re.sub(r'\s+', '_', s.lower())
        s = re.sub(r'[^a-z0-9./\_]', '', s)
        return re.sub(r'[_]+', '_', s)
    else:
        return ''


# --------------------------------------------------
def test_normalize() -> None:
    """" Test normalize """

    assert normalize(None) == None
    assert normalize('') == None
    assert normalize('Foo Bar') == 'foo_bar'
    assert normalize('Foo / Bar') == 'foo_bar'
    assert normalize('Foo (Bar)') == 'foo_bar'
    assert normalize('FooBarBAZ') == 'foo_bar_baz'


# --------------------------------------------------
if __name__ == '__main__':
    main()
