![Static Badge](https://img.shields.io/badge/Python-orange)
![PyPI - Version](https://img.shields.io/pypi/v/steam-vdf)
![GitHub License](https://img.shields.io/github/license/mdeguzis/steam-vdf)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/mdeguzis/steam-vdf/python-app.yml)


# Steam VDF Tool

A command-line utility for managing Steam library data, non-Steam game shortcuts, and analyzing Steam storage usage.

## Features

- Display Steam library information and user accounts
- List and manage non-Steam game shortcuts
- Analyze storage usage of Steam and non-Steam directories
- Export VDF files to JSON format (for valid types)
- Binary VDF file support
- Restart Steam service
- Analyze storage of Steam and Non-Steam games

## Installation

It is recommended to use pipx for system isolation best practices. 
```
pipx install steam-vdf
```

If you must use pip:

```
pip install steam-vdf
```

## Usage

```
steam-vdf --help
```

Some commands (such as info), have additional help information:
```
steam-vdf info --help
```

## Development

### Install

Install a local version with:
```
# Install using pipenv (recommended)
pipenv install --dev
pipenv shell
```

### Build docs
```
make docs
```

### Distribute

Build
```
make
```

Upload
```
make updload
```

https://packaging.python.org/en/latest/tutorials/packaging-projects/
