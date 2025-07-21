#!/usr/bin/env python3

import sys
import yaml
import re

# List of allowed keywords that can be used between [] in the description field
# Add more allowed keywords as needed
ALLOWED_KEYWORDS = {
    "MON", "TEST"
}

def check_description_keywords(data):
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
                if keyword not in ALLOWED_KEYWORDS:
                    errors.append(
                        f"network_ports[{idx}].description: Keyword '{keyword}' is not allowed. Allowed: {sorted(ALLOWED_KEYWORDS)}"
                    )
    return errors

def main():
    for file in sys.argv[1:]:
        with open(file, "r") as f:
            try:
                data = yaml.safe_load(f)
            except Exception as e:
                print(f"YAML parsing error in {file}: {e}")
                sys.exit(1)
            errors = check_description_keywords(data)
            if errors:
                print(f"Errors in {file}:")
                for err in errors:
                    print("  " + err)
                sys.exit(1)

if __name__ == "__main__":
    main()