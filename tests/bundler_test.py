""" Tests for fib.py """

import os
import random
import re
import string
from shutil import rmtree
from subprocess import getstatusoutput

PRG = './3dt_bundler.py'


# --------------------------------------------------
def test_exists() -> None:
    """ Program exists """

    assert os.path.isfile(PRG)


# --------------------------------------------------
def test_usage() -> None:
    """ Usage """

    for flag in ['-h', '--help']:
        rv, out = getstatusoutput(f'{PRG} {flag}')
        assert rv == 0
        assert out.lower().startswith('usage:')


# --------------------------------------------------
def test_bad_indir() -> None:
    """ Dies when given bad input directory """

    bad = random_string()
    rv, out = getstatusoutput(f'{PRG} -i {bad} -o out')
    assert rv != 0
    assert out.lower().startswith('usage:')
    assert re.search(f'--indir "{bad}" is not a directory', out)


# --------------------------------------------------
def test_runs_ok() -> None:
    """ Runs OK """

    out_dir = random_string()
    if os.path.isdir(out_dir):
        rmtree(out_dir)

    try:
        rv, out = getstatusoutput(f'{PRG} -o {out_dir} -i tests/inputs')
        assert rv == 0
        assert os.path.isdir(out_dir)
        assert os.path.isdir(os.path.join(out_dir, 'dir1'))
        assert os.path.isdir(os.path.join(out_dir, 'dir_two'))
        assert os.path.isfile(os.path.join(out_dir, 'take1.csv'))
        assert os.path.isfile(os.path.join(out_dir, 'dir1', 'take2.csv'))
        assert os.path.isfile(os.path.join(out_dir, 'dir_two', 'a_file.txt'))
        assert not os.path.isfile(os.path.join(out_dir, 'empty.csv'))
        assert not os.path.isfile(os.path.join(out_dir, 'audio1.wav'))
        assert not os.path.isfile(os.path.join(out_dir, 'data.zip'))
        assert not os.path.isfile(os.path.join(out_dir, 'audio2.mp3'))
    finally:
        if os.path.isdir(out_dir):
            rmtree(out_dir)


# --------------------------------------------------
def random_string() -> str:
    """ Generate a random string """

    k = random.randint(5, 10)
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=k))
