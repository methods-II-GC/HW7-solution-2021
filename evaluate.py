#!/usr/bin/env python
"""Evaluates anagram decoding."""

import argparse
import logging


def main(args: argparse.Namespace) -> None:
    tokens = 0
    correct_tokens = 0
    sentences = 0
    correct_sentences = 0
    with open(args.gold, "r") as gold, open(args.hypo, "r") as hypo:
        for (lineno, (gold_line, hypo_line)) in enumerate(zip(gold, hypo), 1):
            gold_tokens = gold_line.split()
            hypo_tokens = hypo_line.split()
            if len(gold_tokens) != len(hypo_tokens):
                logging.error("Length mismatch at line %d", lineno)
                exit(1)
            correct_sentence = True
            for (gold_token, hypo_token) in zip(gold_tokens, hypo_tokens):
                if gold_token == hypo_token:
                    correct_tokens += 1
                else:
                    correct_sentence = False
                tokens += 1
            correct_sentences += correct_sentence
            sentences += 1
    print(f"Word accuracy:\t\t{100 * correct_tokens / tokens:.2f}%")
    print(f"Sentence accuracy:\t{100 * correct_sentences / sentences:.2f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gold", help="path to gold input file")
    parser.add_argument("hypo", help="path to hypothesis input file")
    main(parser.parse_args())
