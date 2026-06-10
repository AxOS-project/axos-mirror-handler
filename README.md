# AxOS Mirror Handler

A simple script that allows you to list, add, and remove packages from the [AxOS-Project/AxMirrors](https://github.com/AxOS-Project/AxMirrors) GitHub repository.

## Requirements

- Create a `TOKEN.txt` file.
- Put your GitHub token that has Read, Write permissions enabled in the `TOKEN.txt` file.

## Usage

**List all packages:**

```sh
$ python3 mirror.py list
```

**Add a package:**

```sh
$ python3 mirror.py add <path/to/file>
```

**Remove a package:**

```sh
$ python3 mirror.py remove <filename>
```
