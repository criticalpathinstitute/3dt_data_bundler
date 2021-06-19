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
import hashlib
from shutil import copy
from pathlib import Path
from subprocess import getstatusoutput
from typing import List, NamedTuple, Optional, TextIO


class Args(NamedTuple):
    """ Command-line arguments """
    dirs: List[str]
    out_dir: str
    skip_exts: List[str]


# --------------------------------------------------
def get_args() -> Args:
    """ Get command-line arguments """

    parser = argparse.ArgumentParser(
        description='Data bundler for 3DT data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('dirs',
                        metavar='DIR',
                        help='Input directories',
                        nargs='+')

    parser.add_argument('-o',
                        '--outdir',
                        metavar='DIR',
                        help='Output directory',
                        default='out')

    parser.add_argument('-s',
                        '--skip_exts',
                        metavar='STR',
                        help='Extensions for files to skip',
                        nargs='+',
                        default=['.wav', '.mp3', '.mp4', '.zip', '.pyc'])

    args = parser.parse_args()

    if bad := list(filter(lambda d: not os.path.isdir(d), args.dirs)):
        parser.error(f'Invalid directory: {", ".join(bad)}')

    out_dir = normalize(args.outdir)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    return Args(dirs=args.dirs, out_dir=out_dir, skip_exts=args.skip_exts)


# --------------------------------------------------
def main() -> None:
    """ Make a jazz noise here """

    args = get_args()
    checksums_fh = open(os.path.join(args.out_dir, 'checksums.md5'), 'wt')
    num_copied, num_total = 0, 0

    for dirname in args.dirs:
        in_dir = os.path.abspath(dirname)
        files = filter(Path.is_file, Path(in_dir).rglob('*'))

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
            dest = os.path.join(new_dir, basename)
            copy(path, dest)
            print('{} {}'.format(
                hashlib.md5(open(dest, 'rb').read()).hexdigest(),
                os.path.join(relative_dir, basename)),
                  file=checksums_fh)
            num_copied += 1

    checksums_fh.close()
    zip_file = f'{args.out_dir}.zip'
    rv, _ = getstatusoutput(f'zip -r {zip_file} {args.out_dir}')
    if rv != 0:
        sys.exit('Error zipping "{args.out_dir}"!')

    print(f'Done, copied {num_copied:,} of {num_total:,} into "{zip_file}".')


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
