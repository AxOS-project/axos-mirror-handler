#!/usr/bin/env python3
import sys
import os
import base64
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# Argument definition
parser = argparse.ArgumentParser(
    prog="axmirrors",
    description="Push files to AxMirrors"
)
parser.add_argument("--token-file", default="~/.config/axmirror/TOKEN.txt", metavar="PATH", help="Path to token file")

subparsers = parser.add_subparsers(dest="command")
subparsers.add_parser("list", help="List files in AxMirrors")
add_parser = subparsers.add_parser("add", help="Add a file to AxMirrors")
add_parser.add_argument("path", help="Path to file")
remove_parser = subparsers.add_parser("remove", help="Remove a file from AxMirrors")
remove_parser.add_argument("name", help="Filename to remove")
subparsers.add_parser("config", help="Show current configuration")

args = parser.parse_args()

if args.token_file:
    token_path = Path(args.token_file)
    expanded_path = token_path.expanduser()

    if not os.path.isfile(expanded_path):
        print(f"Token file not found: {args.token_file}")
        res = ""

        while res.lower() not in ("y", "n"):
            res = input("Would you like to initialize it? [y/N] ").strip()

        match (res.lower()):
            case "y":
                print("Please enter your TOKEN:")
                token = input("").strip()
                expanded_path.parent.mkdir(parents=True, exist_ok=True)
                with open(expanded_path, "w") as file:
                    file.write(token)
                    print("Successfully saved your TOKEN!")
                    print("NOTE: Your TOKEN is stored in plain text.")

            case "n":
                sys.exit(0);
            case _:
                sys.exit(1);

    with open(expanded_path) as f:
        TOKEN = f.read().strip()

# Config
REPO     = "AxOS-Project/AxMirrors"
BRANCH   = "main"
PKG_PATH = "x86_64"

# Code
API = f"https://api.github.com/repos/{REPO}"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "application/json",
}

def request(method, endpoint, data=None):
    url = f"{API}{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, method=method, headers=HEADERS, data=body)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}")
        sys.exit(1)

def get_file_sha(name):
    """Fetch the blob SHA of an existing file, or None if it doesn't exist."""
    encoded = urllib.parse.quote(f"{PKG_PATH}/{name}", safe="")
    params = urllib.parse.urlencode({"ref": BRANCH})
    url = f"{API}/contents/{encoded}?{params}"
    req = urllib.request.Request(url, method="GET", headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())["sha"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        print(f"HTTP {e.code}: {e.read().decode()}")
        sys.exit(1)

def cmd_list():
    encoded_path = urllib.parse.quote(PKG_PATH, safe="")
    params = urllib.parse.urlencode({"ref": BRANCH})
    items = request("GET", f"/contents/{encoded_path}?{params}")
    files = [i for i in items if i["type"] == "file"]
    if not files:
        print("No packages found.")
    else:
        for f in files:
            print(f["name"])

def cmd_add(filepath):
    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)
    name = os.path.basename(filepath)
    encoded = urllib.parse.quote(f"{PKG_PATH}/{name}", safe="")
    print(f"Uploading {name} ...")
    with open(filepath, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    body = {
        "message": f"mirror: add {name}",
        "content": content,
        "branch": BRANCH,
    }
    sha = get_file_sha(name)
    if sha:
        body["sha"] = sha  # required for updates
    request("PUT", f"/contents/{encoded}", body)
    print(f"Done: {name} {'updated' if sha else 'added'}.")

def cmd_remove(name):
    encoded = urllib.parse.quote(f"{PKG_PATH}/{name}", safe="")
    sha = get_file_sha(name)
    if not sha:
        print(f"File not found in repo: {name}")
        sys.exit(1)
    print(f"Removing {name} ...")
    request("DELETE", f"/contents/{encoded}", {
        "message": f"mirror: remove {name}",
        "sha": sha,
        "branch": BRANCH,
    })
    print(f"Done: {name} removed.")

def cmd_config():
    print("Mirror Config:")
    print(f"- repo: {REPO}")
    print(f"- branch: {BRANCH}")
    print(f"- pkg_path: {PKG_PATH}")

# Argument handling
match args.command:
    case "list":    cmd_list()
    case "add":     cmd_add(args.path)
    case "remove":  cmd_remove(args.name)
    case "config":  cmd_config()
    case _:         parser.print_help(); sys.exit(1)
