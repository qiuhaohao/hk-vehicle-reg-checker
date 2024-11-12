# Hong Kong Vehicle Registration Mark Checker

A command-line tool to check the availability status of Hong Kong vehicle registration marks from the Transport Department website.

## Features

- Query multiple vehicle registration marks in one session
- Automatic Chrome driver management
- Save HTML results for each query
- Analyze results in CSV format
- Validation for valid registration mark prefixes
- Headless mode support for automated checking
- Skip checking unavailable prefixes

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/qiuhaohao/hk-vehicle-reg-checker.git
   cd hk-vehicle-reg-checker
   ```

2. Set up a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Query Registration Marks

Run the script with the following command:
```sh
python main.py [OPTIONS] [PLATES...]
```

Options:
- `-o`, `--output`: Directory to save HTML results (default: "output")
- `--skip-unavailable`: Skip checking plates that are not available for reservation
- `--headless`: Run Chrome in headless mode

Arguments:
- `PLATES`: One or more plate numbers in format XX9999 (e.g., BD8374 ZZ1234)

### Analyze Results

After querying, analyze the results using:
```sh
./analyze_results.sh <file_path> [<file_path> ...]
```

This will generate a CSV with columns:
- `plate`: Registration mark
- `status`: Current status (available/reserved/allocated/processing/other)
- `update_time`: Last check timestamp

You can use wildcards to specify multiple files, for example:
```sh
./analyze_results.sh output/*
./analyze_results.sh output/*1234.html
./analyze_results.sh output/AB*.html
```

### Examples

#### Check multiple available registration marks
This script is best used in combination with bash brace expansion to check multiple plates.
```sh
python main.py --skip-unavailable {A..Z}{A..Z}1234
```
This checks the status of available registration marks from AA1234 to ZZ1234, saving results to "./output".
