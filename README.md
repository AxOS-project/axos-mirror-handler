# AxOS Mirror Handler

A simple script that allows you to list, add, and remove packages from the [AxOS-Project/AxMirrors](https://github.com/AxOS-Project/AxMirrors) GitHub repository.

## Installation

Run the install script to copy the `mirror.py` file to `~/local/bin/axmirrors`.

```sh
$ ./install.sh
```

## Usage

Assumes that you've already downloaded the script.

**List all packages:**

```sh
$ axmirrors list
```

**Add a package:**

```sh
$ axmirrors add <path/to/file>
```

**Remove a package:**

```sh
$ axmirrors remove <filename>
```

**Shadow a package:**

```sh
$ axmirrors shadow <path/to/file>
```

**View Config:**

```sh
$ axmirrors config
```
