#!/usr/bin/env python3
import os
import re
import sys
import argparse
import configparser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--grammar-dir", required=True, help="Output directory for JSGF grammars"
    )
    parser.add_argument(
        "--ini-file", default=None, help="Path to ini file (default=stdin)"
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Don't overwrite existing grammar files",
    )
    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.grammar_dir, exist_ok=True)

    # Create ini parser
    config = configparser.ConfigParser(
        allow_no_value=True, strict=False, delimiters=["="]
    )

    config.optionxform = lambda x: str(x)  # case sensitive

    if args.ini_file:
        # Read from file
        with open(args.ini_file, "r") as ini_file:
            config.read_file(ini_file)
    else:
        # Read from stdin
        config.read_file(sys.stdin)

    # Process configuration sections
    grammar_rules = {}

    for sec_name in config.sections():
        sentences: List[str] = []
        rules: List[str] = []
        for k, v in config[sec_name].items():
            if v is None:
                # Collect non-valued keys as sentences
                sentences.append("({0})".format(k.strip()))
            else:
                # Collect key/value pairs as JSGF rules
                rule = "<{0}> = ({1});".format(k, v)
                rules.append(rule)

        if len(sentences) > 0:
            # Combine all sentences into one big rule (same name as section)
            sentences_rule = "public <{0}> = ({1});".format(
                sec_name, " | ".join(sentences)
            )
            rules.insert(0, sentences_rule)

        grammar_rules[sec_name] = rules

    # Write JSGF grammars
    for name, rules in grammar_rules.items():
        grammar_path = os.path.join(args.grammar_dir, "{0}.gram".format(name))

        # Only overwrite grammar file if it contains rules or doesn't yet exist
        if (len(rules) > 0) or not os.path.exists(grammar_path) or not args.overwrite:
            with open(grammar_path, "w") as grammar_file:
                # JSGF header
                print(f"#JSGF V1.0;", file=grammar_file)
                print("grammar {0};".format(name), file=grammar_file)
                print("", file=grammar_file)

                # Grammar rules
                for rule in rules:
                    # Handle special case where sentence starts with ini
                    # reserved character '['. In this case, use '\[' to pass
                    # it through to the JSGF grammar, where we deal with it
                    # here.
                    rule = re.sub(r"\\\[", "[", rule)
                    print(rule, file=grammar_file)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
