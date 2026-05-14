#!/usr/bin/env python3

import sys
import os
import base64
import json
import urllib.request
import urllib.parse
import urllib.error

# Config
PROJECT_ID = "AxOS-Project/AxMirrors"
BRANCH     = "main"
PKG_PATH   = "x86_64"

with open("TOKEN.txt") as f:
    TOKEN = f.read().strip()

# Code
API = f"https://gitlab.com/api/v4/projects/{urllib.parse.quote(PROJECT_ID, safe='')}"
HEADERS = {"PRIVATE-TOKEN": TOKEN, "Content-Type": "application/json"}


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


def cmd_list():
    params = urllib.parse.urlencode({"path": PKG_PATH, "ref": BRANCH, "per_page": 100})
    items = request("GET", f"/repository/tree?{params}")
    blobs = [i for i in items if i["type"] == "blob"]
    if not blobs:
        print("No packages found.")
    else:
        for f in blobs:
            print(f["name"])


def cmd_add(filepath):
    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    name = os.path.basename(filepath)
    encoded_name = urllib.parse.quote(f"{PKG_PATH}/{name}", safe="")

    print(f"Uploading {name} ...")
    with open(filepath, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    request("POST", f"/repository/files/{encoded_name}", {
        "branch": BRANCH,
        "commit_message": f"mirror: add {name}",
        "encoding": "base64",
        "content": content,
    })
    print(f"Done: {name} added.")


def cmd_remove(name):
    encoded_name = urllib.parse.quote(f"{PKG_PATH}/{name}", safe="")
    print(f"Removing {name} ...")
    request("DELETE", f"/repository/files/{encoded_name}", {
        "branch": BRANCH,
        "commit_message": f"mirror: remove {name}",
    })
    print(f"Done: {name} removed.")


def usage():
    print("Usage:")
    print(f"  {sys.argv[0]} list")
    print(f"  {sys.argv[0]} add <path/to/file>")
    print(f"  {sys.argv[0]} remove <filename>")
    sys.exit(1)


match sys.argv[1:]:
    case ["list"]:          cmd_list()
    case ["add", path]:     cmd_add(path)
    case ["remove", name]:  cmd_remove(name)
    case _:                 usage()
