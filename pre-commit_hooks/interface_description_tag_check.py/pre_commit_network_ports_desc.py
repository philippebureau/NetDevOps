#!/usr/bin/env python3

import sys
import yaml
import re
import argparse
import os

def load_keywords_from_file(filepath):
    """
    Loads allowed keywords from a YAML file.
    The YAML file should contain a list under a key like 'allowed_keywords'.
    Example:
    allowed_keywords:
      - MON
      - TEST
      - PROD
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Keyword configuration file not found: {filepath}")

    with open(filepath, 'r') as f:
        config = yaml.safe_load(f)

    if not config or 'allowed_keywords' not in config or not isinstance(config['allowed_keywords'], list):
        raise ValueError(f"Invalid keyword configuration file format: {filepath}. Expected a 'allowed_keywords' list.")

    return set(config['allowed_keywords'])

def check_description_keywords(data, allowed_keywords):
    errors = []
    if "network_ports" not in data:
        return errors

    for idx, port in enumerate(data["network_ports"]):
        desc = port.get("description", "")
        # Find all words in square brackets in the description
        matches = re.findall(r"\[([^\[\]]+)\]", desc)
        for match in matches:
            keywords = [k.strip() for k in match.split(",")]
            for keyword in keywords:
                if keyword not in allowed_keywords:
                    errors.append(
                        f"network_ports[{idx}].description: Keyword '{keyword}' is not allowed. Allowed: {sorted(allowed_keywords)}"
                    )
    return errors

def main():
    parser = argparse.ArgumentParser(
        description="Pre-commit hook to check allowed keywords in YAML descriptions."
    )
    parser.add_argument(
        "--allowed_list",
        type=str,
        required=True,
        help="Path to the YAML file containing allowed keywords (e.g., pre_commit_data/keyword_list.yml)",
    )
    parser.add_argument(
        'files_to_check',
        nargs='*',
        help='List of files to check (supplied by pre-commit).'
    )

    args = parser.parse_args()

    try:
        allowed_keywords_set = load_keywords_from_file(args.allowed_list)
    except (FileNotFoundError, ValueError) as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while loading keywords: {e}", file=sys.stderr)
        sys.exit(1)

    if not allowed_keywords_set:
        print("Warning: No allowed keywords loaded from the configuration file. The hook will not enforce any keywords.", file=sys.stderr)

    for file in args.files_to_check:
        with open(file, "r") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"YAML parsing error in {file}: {e}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"An unexpected error occurred while processing {file}: {e}", file=sys.stderr)
                sys.exit(1)

            errors = check_description_keywords(data, allowed_keywords_set)
            if errors:
                print(f"Errors in {file}:", file=sys.stderr)
                for err in errors:
                    print("  " + err, file=sys.stderr)
                sys.exit(1)

if __name__ == "__main__":
    main()
