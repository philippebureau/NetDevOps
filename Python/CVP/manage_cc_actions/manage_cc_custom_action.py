#!/usr/bin/env python3
"""
Add or update a Change Control custom action on CVP.

Uses the Resource API REST gateway to manage actions:
  - Create a new custom action from a Python script file
  - Update an existing action (body, args, name, description)
  - List existing custom actions

Usage:
    # List all custom actions
    python3 manage_cc_custom_action.py --host 192.168.0.5 --username cvpadmin list

    # Create a new custom action from a script file
    python3 manage_cc_custom_action.py --host 192.168.0.5 --username cvpadmin create \
        --name "My Action" --script-file path/to/script.py --description "Does something"

    # Update an existing action's script
    python3 manage_cc_custom_action.py --host 192.168.0.5 --username cvpadmin update \
        --action-id <uuid> --script-file path/to/updated_script.py

    # Create or update by name (updates if name already exists)
    python3 manage_cc_custom_action.py --host 192.168.0.5 --username cvpadmin upsert \
        --name "My Action" --script-file path/to/script.py

    # Use a service account token instead of user/pass
    python3 manage_cc_custom_action.py --token <token> --host 192.168.0.5 create \
        --name "My Action" --script-file path/to/script.py
"""

import argparse
import json
import sys
import uuid
from getpass import getpass

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_HOST = "192.168.0.5"
DEFAULT_USERNAME = "cvpadmin"
CVAAS_HOSTS = [
    "www.arista.io",                          # United States 1a
    "www.cv-prod-us-central1-b.arista.io",    # United States 1b
    "www.cv-prod-us-central1-c.arista.io",    # United States 1c
    "www.cv-prod-na-northeast1-b.arista.io",  # Canada
    "www.cv-prod-euwest-2.arista.io",         # Europe West 2
    "www.cv-prod-apnortheast-1.arista.io",    # Japan
    "www.cv-prod-ausoutheast-1.arista.io",    # Australia
    "www.cv-prod-uk-1.arista.io",             # United Kingdom
]

RESOURCE_BASE = "/api/resources/action/v1"

ACTION_LANGUAGES = {
    "python2": 1,
    "python3": 2,
    "go_template": 3,
}

ACTION_LANGUAGE_NAMES = {1: "python2", 2: "python3", 3: "go_template"}

ACTION_TYPE_CC_CUSTOM = 1


def is_cvaas(host):
    return any(host.rstrip("/").endswith(h) for h in CVAAS_HOSTS)


def authenticate(host, username=None, password=None, token=None):
    session = requests.Session()
    base_url = f"https://{host}"

    if is_cvaas(host):
        session.verify = True
        if not token:
            raise RuntimeError(
                "CVaaS requires a service account token (--token). "
                "Username/password auth is not supported."
            )
        session.headers["Authorization"] = f"Bearer {token}"
    else:
        session.verify = False
        if token:
            session.headers["Authorization"] = f"Bearer {token}"
        else:
            resp = session.post(
                f"{base_url}/cvpservice/login/authenticate.do",
                json={"userId": username, "password": password},
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()
            if isinstance(result, dict) and result.get("errorCode"):
                raise RuntimeError(result.get("errorMessage", "authentication failed"))

    return session, base_url


def get_all_actions(session, base_url):
    resp = session.get(f"{base_url}{RESOURCE_BASE}/Action/all", timeout=60)
    resp.raise_for_status()

    actions = []
    for line in resp.text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            value = obj.get("result", {}).get("value", obj)
            actions.append(value)
        except json.JSONDecodeError:
            continue

    return actions


def _unwrap(val):
    """Unwrap a protobuf JSON wrapper like {"value": "x"} to just "x"."""
    if isinstance(val, dict) and "value" in val and len(val) == 1:
        return val["value"]
    return val


def find_action_by_name(actions, name):
    for action in actions:
        core = action.get("core", {})
        if _unwrap(core.get("name")) == name:
            return action
    return None


def find_action_by_id(actions, action_id):
    for action in actions:
        if _unwrap(action.get("key", {}).get("id")) == action_id:
            return action
    return None


def _build_arg_schema(args_dict):
    schema = {}
    for arg_name, arg_def in args_dict.items():
        if not arg_name:
            continue
        definition = {}
        if isinstance(arg_def, dict):
            if "required" in arg_def:
                definition["required"] = bool(arg_def["required"])
            if "default" in arg_def:
                definition["default"] = {"value": str(arg_def["default"])}
            if "description" in arg_def:
                definition["description"] = str(arg_def["description"])
        else:
            definition["default"] = {"value": str(arg_def)}
        schema[arg_name] = definition
    return {"values": schema}


def build_action_config(action_id, name, description, body, language, static_args=None, dynamic_args=None):
    lang_value = ACTION_LANGUAGES.get(language, 2)

    config = {
        "key": {"id": action_id},
        "core": {
            "name": name,
            "type": ACTION_TYPE_CC_CUSTOM,
        },
        "language": lang_value,
        "body": body,
    }

    if description:
        config["core"]["description"] = description

    if static_args:
        config["core"]["staticArgs"] = _build_arg_schema(static_args)

    if dynamic_args:
        config["core"]["dynamicArgs"] = _build_arg_schema(dynamic_args)

    return config


def set_action_config(session, base_url, config):
    resp = session.post(
        f"{base_url}{RESOURCE_BASE}/ActionConfig",
        json=config,
        timeout=30,
    )
    if not resp.ok:
        print(f"ERROR: {resp.status_code} {resp.reason}", file=sys.stderr)
        print(f"  Response: {resp.text}", file=sys.stderr)
        resp.raise_for_status()
    return resp.json()


def delete_action_config(session, base_url, action_id):
    resp = session.delete(
        f"{base_url}{RESOURCE_BASE}/ActionConfig",
        params={"key.id": action_id},
        timeout=30,
    )
    if not resp.ok:
        print(f"ERROR: {resp.status_code} {resp.reason}", file=sys.stderr)
        print(f"  Response: {resp.text}", file=sys.stderr)
        resp.raise_for_status()
    return resp.json()


def cmd_list(session, base_url, args):
    actions = get_all_actions(session, base_url)
    cc_actions = [
        a for a in actions
        if _unwrap(a.get("core", {}).get("type")) in (ACTION_TYPE_CC_CUSTOM, "ACTION_TYPE_CHANGECONTROL_CUSTOM")
    ]

    if not cc_actions:
        print("No custom change control actions found.")
        return

    print(f"{'ID':<40} {'NAME':<35} {'LANGUAGE':<12} {'PACKAGE'}")
    print("=" * 110)
    for action in cc_actions:
        aid = _unwrap(action.get("key", {}).get("id", ""))
        core = action.get("core", {})
        audit = action.get("audit", {})
        name = _unwrap(core.get("name", ""))
        lang = _unwrap(action.get("language", ""))
        if isinstance(lang, int):
            lang = ACTION_LANGUAGE_NAMES.get(lang, str(lang))
        elif isinstance(lang, str):
            lang = lang.replace("ACTION_LANGUAGE_", "").lower()
        pkg = _unwrap(audit.get("fromPackage", audit.get("from_package", "")))
        print(f"  {aid:<38} {name:<35} {lang:<12} {pkg}")

    print(f"\n  Total: {len(cc_actions)} custom action(s)")


def cmd_create(session, base_url, args):
    action_id = args.action_id or str(uuid.uuid4())

    if not args.name:
        print("ERROR: --name is required for create", file=sys.stderr)
        sys.exit(1)
    if not args.script_file:
        print("ERROR: --script-file is required for create", file=sys.stderr)
        sys.exit(1)

    with open(args.script_file, "r") as f:
        body = f.read()

    static_args = None
    dynamic_args = None
    if args.args_file:
        with open(args.args_file, "r") as f:
            args_def = json.load(f)
        static_args = args_def.get("static_args")
        dynamic_args = args_def.get("dynamic_args")

    config = build_action_config(
        action_id=action_id,
        name=args.name,
        description=args.description,
        body=body,
        language=args.language,
        static_args=static_args,
        dynamic_args=dynamic_args,
    )

    print(f"Creating action '{args.name}' (id: {action_id}) ...")
    result = set_action_config(session, base_url, config)
    print(f"Action created successfully.")
    print(f"  ID: {action_id}")
    if args.verbose:
        print(json.dumps(result, indent=2))


def cmd_update(session, base_url, args):
    actions = get_all_actions(session, base_url)

    if args.action_id:
        existing = find_action_by_id(actions, args.action_id)
        if not existing:
            print(f"ERROR: No action found with id '{args.action_id}'", file=sys.stderr)
            sys.exit(1)
    elif args.name:
        existing = find_action_by_name(actions, args.name)
        if not existing:
            print(f"ERROR: No action found with name '{args.name}'", file=sys.stderr)
            sys.exit(1)
    else:
        print("ERROR: --action-id or --name is required for update", file=sys.stderr)
        sys.exit(1)

    action_id = _unwrap(existing["key"]["id"])
    core = existing.get("core", {})
    name = args.name or _unwrap(core.get("name", ""))
    description = args.description if args.description is not None else _unwrap(core.get("description", ""))

    if args.script_file:
        with open(args.script_file, "r") as f:
            body = f.read()
    else:
        body = _unwrap(existing.get("body", ""))

    lang = args.language
    existing_lang = _unwrap(existing.get("language", ""))
    if isinstance(existing_lang, int):
        existing_lang = ACTION_LANGUAGE_NAMES.get(existing_lang, "python3")
    elif isinstance(existing_lang, str):
        existing_lang = existing_lang.replace("ACTION_LANGUAGE_", "").lower()
    if lang == "python3" and existing_lang:
        lang = existing_lang

    static_args = None
    dynamic_args = None
    if args.args_file:
        with open(args.args_file, "r") as f:
            args_def = json.load(f)
        static_args = args_def.get("static_args")
        dynamic_args = args_def.get("dynamic_args")

    config = build_action_config(
        action_id=action_id,
        name=name,
        description=description,
        body=body,
        language=lang,
        static_args=static_args,
        dynamic_args=dynamic_args,
    )

    print(f"Updating action '{name}' (id: {action_id}) ...")
    result = set_action_config(session, base_url, config)
    print(f"Action updated successfully.")
    if args.verbose:
        print(json.dumps(result, indent=2))


def cmd_upsert(session, base_url, args):
    if not args.name:
        print("ERROR: --name is required for upsert", file=sys.stderr)
        sys.exit(1)
    if not args.script_file:
        print("ERROR: --script-file is required for upsert", file=sys.stderr)
        sys.exit(1)

    actions = get_all_actions(session, base_url)
    existing = find_action_by_name(actions, args.name)

    if existing:
        args.action_id = _unwrap(existing["key"]["id"])
        print(f"Found existing action '{args.name}', updating ...")
        cmd_update(session, base_url, args)
    else:
        print(f"No existing action named '{args.name}', creating ...")
        cmd_create(session, base_url, args)


def cmd_delete(session, base_url, args):
    if not args.action_id and not args.name:
        print("ERROR: --action-id or --name is required for delete", file=sys.stderr)
        sys.exit(1)

    if args.name and not args.action_id:
        actions = get_all_actions(session, base_url)
        existing = find_action_by_name(actions, args.name)
        if not existing:
            print(f"ERROR: No action found with name '{args.name}'", file=sys.stderr)
            sys.exit(1)
        args.action_id = _unwrap(existing["key"]["id"])

    print(f"Deleting action (id: {args.action_id}) ...")
    result = delete_action_config(session, base_url, args.action_id)
    print("Action deleted successfully.")
    if args.verbose:
        print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Manage Change Control custom actions on CVP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="CVP host address")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help="CVP username")
    parser.add_argument("--password", help="CVP password (prompted if not provided)")
    parser.add_argument("--token", help="Service account token (alternative to user/pass)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print full API responses")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    subparsers.required = True

    # list
    subparsers.add_parser("list", help="List all custom change control actions")

    # create
    p_create = subparsers.add_parser("create", help="Create a new custom action")
    p_create.add_argument("--name", required=True, help="Action name")
    p_create.add_argument("--script-file", required=True, help="Path to the Python script")
    p_create.add_argument("--description", default="", help="Action description")
    p_create.add_argument(
        "--language", default="python3",
        choices=list(ACTION_LANGUAGES.keys()),
        help="Script language (default: python3)",
    )
    p_create.add_argument("--action-id", help="Explicit UUID (auto-generated if omitted)")
    p_create.add_argument(
        "--args-file",
        help="JSON file defining static_args and/or dynamic_args",
    )

    # update
    p_update = subparsers.add_parser("update", help="Update an existing custom action")
    p_update.add_argument("--action-id", help="Action UUID to update")
    p_update.add_argument("--name", help="Action name (used to find action if no --action-id)")
    p_update.add_argument("--script-file", help="Path to the updated Python script")
    p_update.add_argument("--description", default=None, help="Updated description")
    p_update.add_argument(
        "--language", default="python3",
        choices=list(ACTION_LANGUAGES.keys()),
        help="Script language",
    )
    p_update.add_argument("--args-file", help="JSON file defining updated args")

    # upsert
    p_upsert = subparsers.add_parser(
        "upsert", help="Create or update an action by name"
    )
    p_upsert.add_argument("--name", required=True, help="Action name")
    p_upsert.add_argument("--script-file", required=True, help="Path to the Python script")
    p_upsert.add_argument("--description", default="", help="Action description")
    p_upsert.add_argument(
        "--language", default="python3",
        choices=list(ACTION_LANGUAGES.keys()),
        help="Script language (default: python3)",
    )
    p_upsert.add_argument("--action-id", help="Explicit UUID for new actions")
    p_upsert.add_argument("--args-file", help="JSON file defining args")

    # delete
    p_delete = subparsers.add_parser("delete", help="Delete a custom action")
    p_delete.add_argument("--action-id", help="Action UUID to delete")
    p_delete.add_argument("--name", help="Action name (used to find action if no --action-id)")

    args = parser.parse_args()

    if not args.token:
        password = args.password or getpass(f"Password for {args.username}@{args.host}: ")
    else:
        password = None

    print(f"Connecting to CVP at {args.host} ...")
    try:
        session, base_url = authenticate(
            args.host,
            username=args.username,
            password=password,
            token=args.token,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print("Authenticated.\n")

    commands = {
        "list": cmd_list,
        "create": cmd_create,
        "update": cmd_update,
        "upsert": cmd_upsert,
        "delete": cmd_delete,
    }
    commands[args.command](session, base_url, args)


if __name__ == "__main__":
    main()
