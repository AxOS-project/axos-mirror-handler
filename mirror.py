#!/usr/bin/env python3
import sys
import os
import base64
import json
import urllib.request
import urllib.parse
import urllib.error

# Config
REPO   = "AxOS-Project/AxMirrors"
BRANCH = "main"
PKG_PATH = "x86_64"

with open("TOKEN.txt") as f:
    TOKEN = f.read().strip()

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
