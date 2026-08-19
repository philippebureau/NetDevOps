# Manage Change Control Custom Actions on CVP / CVaaS

Script: `CVP/manage_cc_custom_action.py`

Manage Change Control custom actions on Arista CloudVision Portal (on-prem CVP or CVaaS) via the Resource API REST gateway. Supports creating, updating, upserting, listing, and deleting custom actions.

## Prerequisites

- Python 3.7+
- `requests` library (`pip install requests`)
- Network access to the CVP/CVaaS instance (HTTPS, port 443)
- On-prem CVP: user credentials or a service account token
- CVaaS: a service account token (username/password is not supported)

## Authentication

### On-prem CVP

**Username/password** (prompted if `--password` is omitted):

```bash
python3 CVP/manage_cc_custom_action.py --host 192.168.0.5 --username cvpadmin list
```

**Service account token:**

```bash
python3 CVP/manage_cc_custom_action.py --host 192.168.0.5 --token <service-account-token> list
```

### CVaaS (CloudVision as a Service)

CVaaS requires a service account token -- username/password auth is not available. The script auto-detects all CVaaS regional hosts and enforces token auth with proper TLS verification.

```bash
python3 CVP/manage_cc_custom_action.py --host www.arista.io --token <service-account-token> list
```

Use the `--host` value matching your CVaaS region:

| Region | Host |
|--------|------|
| United States 1a | `www.arista.io` |
| United States 1b | `www.cv-prod-us-central1-b.arista.io` |
| United States 1c | `www.cv-prod-us-central1-c.arista.io` |
| Canada | `www.cv-prod-na-northeast1-b.arista.io` |
| Europe West 2 | `www.cv-prod-euwest-2.arista.io` |
| Japan | `www.cv-prod-apnortheast-1.arista.io` |
| Australia | `www.cv-prod-ausoutheast-1.arista.io` |
| United Kingdom | `www.cv-prod-uk-1.arista.io` |

To create a service account token in CVaaS, go to **Settings > Access Control > Service Accounts** in the CVaaS UI.

### Global flags

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `192.168.0.5` | CVP host or CVaaS endpoint (e.g. `www.arista.io`) |
| `--username` | `cvpadmin` | CVP username (on-prem only) |
| `--password` | *(prompted)* | CVP password (on-prem only) |
| `--token` | | Service account token (required for CVaaS, optional for on-prem) |
| `--verbose` / `-v` | | Print full API responses |

## Commands

### `list` -- List all custom actions

Shows all actions of type `ACTION_TYPE_CHANGECONTROL_CUSTOM` with their ID, name, language, and package origin.

```bash
python3 CVP/manage_cc_custom_action.py --host 192.168.0.5 --username cvpadmin list
```

Example output:

```
ID                                       NAME                                LANGUAGE     PACKAGE
==============================================================================================================
  a1b2c3d4-e5f6-7890-abcd-ef1234567890   Validate BGP Neighbors              python3      
  f9e8d7c6-b5a4-3210-fedc-ba0987654321   Pre-check Interfaces                python3      com.arista.campus
```

### `create` -- Create a new custom action

Uploads a Python script as a new custom action on CVP.

```bash
python3 CVP/manage_cc_custom_action.py --host 192.168.0.5 --username cvpadmin create \
    --name "Validate BGP Neighbors" \
    --script-file scripts/validate_bgp.py \
    --description "Checks all BGP sessions are Established before proceeding"
```

| Flag | Required | Description |
|------|----------|-------------|
| `--name` | Yes | Display name for the action in CVP |
| `--script-file` | Yes | Path to the Python script file |
| `--description` | No | Description shown in the CVP UI |
| `--language` | No | `python3` (default), `python2`, or `go_template` |
| `--action-id` | No | Explicit UUID; auto-generated if omitted |
| `--args-file` | No | JSON file defining action arguments (see below) |

### `update` -- Update an existing action

Looks up the action by `--action-id` or `--name`, then applies changes. Fields not provided are preserved from the existing action.

```bash
# Update by name
python3 CVP/manage_cc_custom_action.py --host 192.168.0.5 --username cvpadmin update \
    --name "Validate BGP Neighbors" \
    --script-file scripts/validate_bgp_v2.py

# Update by ID
python3 CVP/manage_cc_custom_action.py --host 192.168.0.5 --username cvpadmin update \
    --action-id a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
    --script-file scripts/validate_bgp_v2.py \
    --description "Updated: now also checks BFD status"
```

| Flag | Required | Description |
|------|----------|-------------|
| `--action-id` | One of these | UUID of the action to update |
| `--name` | One of these | Name of the action to update |
| `--script-file` | No | Updated script file (keeps existing if omitted) |
| `--description` | No | Updated description (keeps existing if omitted) |
| `--language` | No | Override the script language |
| `--args-file` | No | Updated argument definitions |

### `upsert` -- Create or update by name

If an action with the given `--name` exists, it is updated. Otherwise a new action is created. This is the recommended command for CI/CD pipelines.

```bash
python3 CVP/manage_cc_custom_action.py --host 192.168.0.5 --username cvpadmin upsert \
    --name "Validate BGP Neighbors" \
    --script-file scripts/validate_bgp.py \
    --description "Checks all BGP sessions are Established"
```

| Flag | Required | Description |
|------|----------|-------------|
| `--name` | Yes | Action name to match or create |
| `--script-file` | Yes | Path to the Python script file |
| `--description` | No | Action description |
| `--language` | No | `python3` (default), `python2`, or `go_template` |
| `--action-id` | No | UUID for new actions (auto-generated if omitted) |
| `--args-file` | No | JSON file defining action arguments |

### `delete` -- Delete a custom action

```bash
# Delete by name
python3 CVP/manage_cc_custom_action.py --host 192.168.0.5 --username cvpadmin delete \
    --name "Validate BGP Neighbors"

# Delete by ID
python3 CVP/manage_cc_custom_action.py --host 192.168.0.5 --username cvpadmin delete \
    --action-id a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

## Action Arguments

Custom actions can define **static arguments** (fixed across all runs) and **dynamic arguments** (set per-run, e.g. when adding the action to a change control stage). Define them in a JSON file and pass it with `--args-file`.

### Args file format

```json
{
  "static_args": {
    "device_ip": {
      "required": true,
      "description": "Target device IP address"
    },
    "timeout": {
      "default": "30",
      "description": "Timeout in seconds"
    }
  },
  "dynamic_args": {
    "run_mode": {
      "default": "check",
      "description": "Run mode: check or apply"
    }
  }
}
```

Each argument supports:

| Field | Type | Description |
|-------|------|-------------|
| `required` | bool | Whether the argument must be provided |
| `default` | string | Default value if not provided |
| `description` | string | Description shown in the CVP UI |

You can also use a shorthand where the value is the default directly:

```json
{
  "static_args": {
    "timeout": "30",
    "retry_count": "3"
  }
}
```

## Examples

### CI/CD pipeline integration

```bash
# Deploy an action from a git repo to CVP on every merge
python3 CVP/manage_cc_custom_action.py \
    --host "$CVP_HOST" \
    --token "$CVP_TOKEN" \
    upsert \
    --name "Pre-change Validation" \
    --script-file actions/pre_change_validation.py \
    --description "Automated pre-change checks" \
    --args-file actions/pre_change_validation_args.json
```

### Bulk deploy multiple actions

```bash
for script in actions/*.py; do
    name=$(basename "$script" .py | tr '_' ' ')
    args_file="${script%.py}_args.json"
    args_flag=""
    [ -f "$args_file" ] && args_flag="--args-file $args_file"

    python3 CVP/manage_cc_custom_action.py \
        --host 192.168.0.5 --token "$CVP_TOKEN" \
        upsert --name "$name" --script-file "$script" $args_flag
done
```

## API Reference

The script uses the CVP Resource API REST gateway, which maps to the `arista.action.v1` gRPC service:

| Operation | HTTP Method | Endpoint |
|-----------|-------------|----------|
| List all actions | `GET` | `/api/resources/action/v1/Action/all` |
| Create/update action | `POST` | `/api/resources/action/v1/ActionConfig` |
| Delete action | `DELETE` | `/api/resources/action/v1/ActionConfig` |

For more details, see the [CloudVision APIs documentation](https://aristanetworks.github.io/cloudvision-apis/) and the [cloudvision-python library](https://github.com/aristanetworks/cloudvision-python).
