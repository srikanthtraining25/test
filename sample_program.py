#!/usr/bin/env python3
"""
A small, self-contained Python sample program.

Features demonstrated:
- Command-line interface with argparse
- Dataclasses and type hints
- Logging with verbosity flag
- Reading from file, STDIN, or a built-in sample
- Basic text processing (tokenization, word frequencies)

Usage examples:
  python sample_program.py --help
  echo "Hello world hello" | python sample_program.py --top 2
  python sample_program.py --file sample_program.py --top 5
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple


WORD_REGEX = re.compile(r"[A-Za-z0-9']+")


@dataclass(frozen=True)
class AppConfig:
    case_sensitive: bool
    top_n: int
    input_path: Path | None
    verbose: bool


@dataclass(frozen=True)
class TextStats:
    num_lines: int
    num_chars: int
    num_words: int
    unique_words: int
    top_words: List[Tuple[str, int]]


def tokenize(text: str, case_sensitive: bool) -> List[str]:
    if not case_sensitive:
        text = text.lower()
    tokens = WORD_REGEX.findall(text)
    logging.debug("Tokenized %d words", len(tokens))
    return tokens


def _builtin_sample_text() -> str:
    return (
        "Python makes it easy to write clean, readable code.\n"
        "This sample counts word frequencies from a text input.\n"
        "You can pass a file, pipe text via STDIN, or use this sample.\n"
        "Python python PYTHON! Readable, reliable, remarkable."
    )


def read_input_text(input_path: Path | None) -> str:
    if input_path is not None:
        logging.debug("Reading from file: %s", input_path)
        try:
            return input_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logging.error("File not found: %s", input_path)
            sys.exit(2)
        except OSError as exc:
            logging.error("Could not read file %s: %s", input_path, exc)
            sys.exit(2)

    if not sys.stdin.isatty():
        logging.debug("Reading from STDIN")
        try:
            data = sys.stdin.read()
        except OSError as exc:
            logging.error("Could not read from STDIN: %s", exc)
            sys.exit(2)

        if data.strip() == "":
            logging.debug("STDIN was empty; using built-in sample text")
            return _builtin_sample_text()
        return data

    logging.debug("Using built-in sample text")
    return _builtin_sample_text()


def compute_stats(text: str, case_sensitive: bool, top_n: int) -> TextStats:
    lines = text.splitlines()
    tokens = tokenize(text, case_sensitive=case_sensitive)
    counter = Counter(tokens)

    num_lines = len(lines)
    num_chars = len(text)
    num_words = len(tokens)
    unique_words = len(counter)
    top_words = counter.most_common(top_n)

    logging.debug(
        "Computed stats: lines=%d chars=%d words=%d unique=%d",
        num_lines,
        num_chars,
        num_words,
        unique_words,
    )

    return TextStats(
        num_lines=num_lines,
        num_chars=num_chars,
        num_words=num_words,
        unique_words=unique_words,
        top_words=top_words,
    )


def format_stats(stats: TextStats) -> str:
    lines = [
        "Text statistics:",
        f"  Lines        : {stats.num_lines}",
        f"  Characters   : {stats.num_chars}",
        f"  Words        : {stats.num_words}",
        f"  Unique words : {stats.unique_words}",
        "  Top words:",
    ]

    if stats.top_words:
        width = max(len(word) for word, _ in stats.top_words)
        for word, count in stats.top_words:
            lines.append(f"    {word:<{width}}  {count}")
    else:
        lines.append("    (none)")

    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze text from a file, STDIN, or a built-in sample and "
            "show word-frequency statistics."
        )
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Path to an input text file (UTF-8)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Show the top N most frequent words (default: 10)",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Treat words with different casing as distinct (default: false)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose debug logging",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    config = AppConfig(
        case_sensitive=bool(args.case_sensitive),
        top_n=int(args.top),
        input_path=args.file,
        verbose=bool(args.verbose),
    )

    text = read_input_text(config.input_path)
    stats = compute_stats(text, case_sensitive=config.case_sensitive, top_n=config.top_n)

    print(format_stats(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
