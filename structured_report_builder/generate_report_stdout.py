#!/usr/bin/env python3
"""
Wrapper script for generate_full_report that outputs to stdout
This is used by the FastAPI backend to capture report content
"""
import sys
import io
from contextlib import redirect_stdout
from generate_full_report import generate_full_report

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_report_stdout.py <stock_id> [exchange]", file=sys.stderr)
        sys.exit(1)

    # Force UTF-8 encoding for both stdout and stderr to handle Unicode characters (₹, etc.)
    utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    utf8_stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    sys.stdout = utf8_stderr  # Temporarily redirect stdout to stderr for progress messages
    sys.stderr = utf8_stderr

    stock_id = int(sys.argv[1])
    exchange = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    # Generate report (progress messages will go to stderr via sys.stdout)
    report = generate_full_report(stock_id, exchange)

    # Print only the report to stdout with UTF-8 encoding
    print(report, file=utf8_stdout, flush=True)
