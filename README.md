# 3DT File Bundler

This program will copy the wanted files from an input directory into an output directory and will create a manifest of the selected files.
Run with `-h|--help` for the usage:

```
$ ./3dt_bundler.py -h
usage: 3dt_bundler.py [-h] -i DIR -o DIR [-m FILE] [-s STR [STR ...]]

Data bundler for 3DT data

optional arguments:
  -h, --help            show this help message and exit
  -i DIR, --indir DIR   Input directory (default: None)
  -o DIR, --outdir DIR  Output directory (default: None)
  -m FILE, --manifest FILE
                        Manifest path (default: manifest.txt)
  -s STR [STR ...], --skip_exts STR [STR ...]
                        Extensions for files to skip (default: ['.wav',
                        '.mp3', '.mp4', '.zip'])
```

All files will be copied except:

* Empty files
* Any file with an extension in the list `--skip_exts`
* H5 files that do not contain Sensors or time information

All files that are skipped will be printed to `STDERR` along with a reason for skipping.
For example, the _tests/inputs_ directory contains the following files:

```
$ tree tests/inputs/
tests/inputs/
├── Dir\ Two
│   └── A\ File.txt
├── audio1.wav
├── audio2.mp3
├── data.zip
├── dir1
│   └── take2.csv
├── empty.txt
└── take1.csv

2 directories, 7 files
```

If you run the program like so:

```
$ ./3dt_bundler.py -i tests/inputs -o out 2>err
    1: Copying take1.csv
    6: Copying take2.csv
    7: Copying a_file.txt
Done, copied 3 of 7 to "out".
See manifest file "manifest.txt".
```

Each file that is copied will be placed into the same relative directory from the input directory.
You will notice that the output directories and files are _normalized_ by lowercasing all the letters, turning spaces into underscores, and removing all non-word characters (and the dot):

```
$ tree out/
out/
├── dir1
│   └── take2.csv
├── dir_two
│   └── a_file.txt
└── take1.csv

2 directories, 3 files
```

The _manifest.txt_ file should contain the relative paths of the selected files:

```
$ cat manifest.txt
take1.csv
dir1/take2.csv
dir_two/a_file.txt
```

You should find that the _err_ file contains reports of the three files that were skipped:

```
$ cat err
/Users/kyclark/work/cpath/3dt_data_bundler/tests/inputs/empty.txt is empty
/Users/kyclark/work/cpath/3dt_data_bundler/tests/inputs/audio2.mp3 is skipped
/Users/kyclark/work/cpath/3dt_data_bundler/tests/inputs/data.zip is skipped
/Users/kyclark/work/cpath/3dt_data_bundler/tests/inputs/audio1.wav is skipped
```

The `--outdir` can contain multiple directories, e.g.:

```
$ ./3dt_bundler.py -i tests/inputs/ -o foo/bar 2>err
    1: Copying take1.csv
    6: Copying take2.csv
    7: Copying a_file.txt
Done, copied 3 of 7 to "foo/bar".
See manifest file "manifest.txt".
$ tree foo/
foo/
└── bar
    ├── dir1
    │   └── take2.csv
    ├── dir_two
    │   └── a_file.txt
    └── take1.csv

3 directories, 3 files
```

## Testing

Run `make test` to run the test suite:

```
$ make test
python3 -m pytest -xv --flake8 --pylint --mypy tests/bundler_test.py
============================= test session starts ==============================
platform darwin -- Python 3.9.1, pytest-6.1.2, py-1.9.0, pluggy-0.13.1 -- /Library/Frameworks/Python.framework/Versions/3.9/bin/python3
cachedir: .pytest_cache
rootdir: /Users/kyclark/work/cpath/3dt_data_bundler
plugins: mypy-0.7.0, flake8-1.0.6, pylint-0.17.0
collected 6 items

tests/bundler_test.py::FLAKE8 SKIPPED                                    [ 14%]
tests/bundler_test.py::mypy PASSED                                       [ 28%]
tests/bundler_test.py::test_exists PASSED                                [ 42%]
tests/bundler_test.py::test_usage PASSED                                 [ 57%]
tests/bundler_test.py::test_bad_indir PASSED                             [ 71%]
tests/bundler_test.py::test_runs_ok PASSED                               [ 85%]
::mypy PASSED                                                            [100%]
===================================== mypy =====================================

Success: no issues found in 1 source file
========================= 6 passed, 1 skipped in 0.35s =========================
```

## Author

Ken Youens-Clark <kyclark@c-path.org>
