"""
CVP Action: Trigger GitHub Repository Dispatch

This action sends a repository_dispatch webhook to GitHub Actions,
allowing CVP to trigger CI/CD pipelines on demand.

Required CVP action arguments which needs to be created in the CVP action:
  - github_token: GitHub Personal Access Token (with repo scope)
  - event_type: The event type string to send (e.g. "avd-validate")
  - repo: GitHub repo in "owner/repo" format
"""

import socket
import requests

def main(ctx):
    token = ctx.action.args.get("github_token", "")
    event_type = ctx.action.args.get("event_type", "")
    repo = ctx.action.args.get("repo", "")

    if not token:
        ctx.error("github_token is required")
        return
    if not event_type:
        ctx.error("event_type is required")
        return
    if not repo:
        ctx.error("repo is required")
        return
    url = f"https://api.github.com./repos/{repo}/dispatches"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {
        "event_type": event_type,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 204:
            ctx.info(f"Repository dispatch triggered successfully (event_type: {event_type})")
        else:
            ctx.error(f"GitHub API error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        ctx.error(f"Connection error: {e}")


main(ctx)
