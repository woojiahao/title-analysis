# title-analysis
Analysis algorithm for Shopee Data Science Challenge

## Installation
```bash
$ pip install pandas click
```

## CLI Documentation
```bash
$ python tool.py --help

Usage: tool.py [OPTIONS]

Options:
  -b, --base TEXT        Compulsory base directory path storing all the files required
  -ca, --category TEXT   Compulsory name of category being analyzed
  -j, --json TEXT        Optional location for .json file, defaults to {base}/{category}.json
  -c, --csv TEXT         Optional location for .csv file, defaults to {base}/{category}.csv
  -o, --out TEXT         Optional output file location, defaults to {base}/out/
  -a, --accuracy TEXT    Optional comma-separated list of columns to output the accuracy for, defaults output nothing
  -m, --mismatches TEXT  Optional path parameter to store mismatch data
  --help                 Show this message and exit.
```