# AxOS Mirror Handler

A simple script that allows you to list, add, and remove packages from the [AxOS-Project/AxMirrors](https://gitlab.com/AxOS-Project/AxMirrors) GitLab repository.

## Requirements

- Create a `TOKEN.txt` file.
- Put your GitLab token that has `api` scope enabled in the `TOKEN.txt` file.

![alt text](.github/image.png)

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
